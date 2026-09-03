# Methodology — how a league-winner thinks at the draft table

This is the reasoning behind every recommendation the skill makes. It's written so you can explain each decision to a novice in one sentence and defend it to a data scientist in three.

Contents

1. The three ideas that do all the work
2. Replacement level: computing it for any league
3. Surplus, and why it's measured in points, not picks
4. Keeper math: cost, market value, inflation, and the flip conditions
5. Pick geometry: snake picks, turns, and what keepers do to the board
6. Availability: Monte Carlo, and the pencil-and-paper shortcut
7. Tiers and cliffs
8. Scarcity by position: what usually holds, and how scoring bends it
9. Reach rules
10. Building projections you can defend
11. Sample drafts and the target build
12. Late rounds: handcuffs and next-year keepers
13. Superflex, 2QB, TE-premium, best ball, auction
14. Sensitivity: the assumption that flips the board
15. Signal versus noise in the room

---

## 1. The three ideas that do all the work

**Surplus, not projection.** A player's value to you is not how many points he scores. It's how many more he scores than the player you'd otherwise start in that slot. A receiver projecting 215 can be a worse pick than a running back projecting 211 if the 44th-best receiver scores 139 and the 40th-best back scores 111. That 28-point gap in replacement level is the single most important number in most leagues, and almost nobody at the table has computed it.

**Price the market you're in.** ADP tells you what a generic drafter pays. Your league is not generic: it has this platform's default rankings pulling on the room, this many teams, these keepers already gone, and these specific humans with their specific habits. A player's "value" is what he costs *here*, at *your* picks. Keeper removals alone can shift the effective board by half a round or more.

**Say the bear case out loud.** Every verdict comes with the strongest argument against it and the one fact that would change it. This is not hedging — it's how you avoid the season-losing mistake, which is almost always a confident pick made without checking the thing that was checkable.

## 2. Replacement level: computing it for any league

Replacement level at a position is the projected total of the worst player who still has to be in someone's starting lineup every week. Above him, players have surplus; below him, they're free.

Compute it from the lineup:

```
starters_at_pos = teams × dedicated slots at that position
flex_allocation = teams × flex slots × share of flex likely filled by that position
N = starters_at_pos + flex_allocation
replacement[pos] = projection of the N-th best player at pos
```

Flex share defaults (from how leagues actually fill flex): RB 55%, WR 40%, TE 5% in half-PPR and standard; RB 45%, WR 50%, TE 5% in full PPR. Superflex/OP slots are filled by QBs ~85% of the time when a QB is available — treat them as an extra QB starter.

Worked example — 14 teams, QB/2RB/2WR/TE/2FLEX/K/DEF, half-PPR:

```
QB:  14 × 1                       = 14   → 14th QB
RB:  14 × 2 + 14 × 2 × 0.55       = 43   → ~42nd RB
WR:  14 × 2 + 14 × 2 × 0.40       = 39   → ~44th WR (round up for injuries/byes)
TE:  14 × 1 + 14 × 2 × 0.05       = 15   → 15th TE
```

Round to what the sim script uses (it takes `replacement_rank` overrides in league.yaml if you disagree). Add 2–4 to RB and WR counts in deep leagues to account for byes and injuries: someone is always starting the 44th receiver in Week 7.

Deeper leagues push replacement down at every position and make scarce positions scarcer; that is why the same player is a round more valuable in a 14-team league than a 10-team league.

## 3. Surplus, and why it's measured in points, not picks

`surplus = projection − replacement[pos]`. Rank the board by it.

Never rank by "picks of value" (ADP minus cost). Points-per-pick is steepest at the top of the board: the gap between WR3 and WR12 overall is far larger than the gap between RB25 and RB35. A keeper who saves you four picks on a top-5 player is worth more than one who saves you twenty picks in round 8. Translate every "he's a steal" claim into projected points over the alternative before you believe it.

Keep the projection and the surplus visible side by side in every table so the reader can see the position effect doing its work.

## 4. Keeper math

For each candidate:

1. **Cost** — the pick number the keeper consumes. Convert the keeper's round to the user's overall pick in that round (snake order). Round-minus-one rules mean a player drafted in round 3 costs the round-2 pick; check `references/keeper-rules.md` for the taxonomy.
2. **Market value** — the player's current ADP on the user's platform, expressed as an overall pick.
3. **Inflation adjustment** — with K keepers removed from the pool before the draft, the player actually on the board at pick p is worse than ADP p suggests. How much worse depends on whether keepers *cost picks*:
   - In leagues where each keeper consumes that team's pick in the keeper's round (same-round, round-minus-one, and similar), inflation is **front-loaded**: keepers are mostly top-60 players, so the top of the board is thinned, but every forfeited pick puts a player back. Net inflation at pick p ≈ (keepers already "ahead" of p) − (forfeited picks before p). Measured by simulation in a 12-team one-keeper league: about +11 at pick 5, +8 at pick 20, +6 at 29, +4 at 44, and roughly zero from round 6 on. So pick 20 delivers the ADP-28 player, and a round-6 pick delivers a true round-6 player.
   - In leagues where keepers are free (no pick forfeited — a fixed last-round cost, or an extra roster slot), inflation is close to K at every pick and doesn't fade.
   - `draft_sim.py` measures the inflation actually in force at each of your picks (`inflation_at_pick`); quote that rather than a rule of thumb whenever you have it.
   - The consequence for keeper valuation: a keeper who costs an early pick is competing against an inflated board (his surplus is a little better than the raw pick-vs-ADP comparison shows); a keeper who costs a mid-round pick is competing against an almost un-inflated board (the raw comparison is about right).
4. **Surplus in points** — projection of the keeper minus projection of the player you'd realistically get with that pick after inflation. This is the number that decides.

Then run the flip checks:

- **Eligibility.** Waiver pickups, traded players, or players kept last year may be ineligible or priced differently. This is the single most common "the whole analysis changes" fact; ask before you compute.
- **Superflex / 2QB.** A QB keeper's surplus roughly doubles because the replacement QB drops from the 12th-best to the 24th-best. Josh Allen at a round-2 cost is a fade in 1QB and an easy keep in superflex.
- **Escalation.** If a kept player's cost rises a round each year, a round-1 keeper has nowhere to go and the "keep him again next year" option is worthless — a mild argument for taking value elsewhere, rarely enough to change this season's call.
- **Keeping nobody.** Always price it. It's usually dominated — you forfeit surplus for nothing — but if every candidate is negative, keeping nobody and drafting the round is correct.
- **Next-year optionality.** A cheap late-round keeper that you can hold for years is worth more than its one-season surplus. Note it; don't let it override a large one-season gap.

Present as a table: Player | Cost (round → pick) | ADP | Surplus in picks | Surplus in points | Verdict. Then the verdict paragraph, the bear case on the chosen keeper, and "the one thing to confirm."

## 5. Pick geometry

Snake draft, T teams, slot s: round r pick is `(r−1)×T + s` when r is odd and `r×T − s + 1` when r is even. Slot 11 of 14: 11, 18, 39, 46, 67, 74, 95, 102, 123, 130, …

Two things to read off the ladder:

- **Turn tightness.** Slots at the ends have paired picks (1 and 28 in a 14-team league; 14 and 15). Middle slots have evenly spaced picks (~14 apart). Paired picks let you plan two-player combinations ("RB + RB at 33/40"); evenly spaced picks mean you cannot count on anyone surviving a full round.
- **Keeper forfeits.** Each team loses the round its keeper cost. Remove those picks from the order. The user's own forfeited round shifts nothing for them but changes what's on the board for everyone else — the sim handles this; by hand, just note that K picks are missing.

`references/draft-slot-playbook.md` walks through early, middle, and late slots by league size.

## 6. Availability: Monte Carlo, and the pencil-and-paper shortcut

**With the script.** `draft_sim.py` removes keepers (weighted toward better players, with keeper rounds correlated to player quality — or the league's published list if you have it), then drafts the other teams on ADP plus noise scaled to each player's observed ADP spread (capped, so deep sleepers aren't drafted in round 5), with a positional-need bias from round 8 on and a realistic K/DEF curve, and records who is on the board at each of the user's picks across 1,500 runs. "There %" is that frequency. Below 50%: plan for him being gone. Above 80%: no reason to reach. The script always reports the user's own players and "my guys" at every pick, and writes a full name × pick availability matrix (`sim_availability.csv`) for anyone else you need to look up.

The "you" in the simulation drafts by surplus, adjusted for lineup need and for the opportunity cost of waiting (it learns, per position, how much surplus is usually still there at your next pick). Its sample drafts are illustrative, not a plan: read them for the patterns that recur, then write the target build yourself.

**Without the script.** Availability at pick p for a player with ADP a and spread σ is approximately `P(available) = 1 − Φ((p_eff − a)/σ_eff)` where Φ is the standard normal CDF, `p_eff = p + inflation at that pick` (from §4), and `σ_eff = max(σ, 4) + 0.15 × inflation` to reflect keeper uncertainty. Quick table for `(p − a_eff)/σ_eff`: −2 → 98%, −1 → 84%, 0 → 50%, +1 → 16%, +2 → 2%. A player with ADP 49, σ 5, at pick 44 with +4 inflation (p_eff 48): z = (48 − 49)/5.6 ≈ −0.2 → ~57% available. A coin flip — take him now if he's the target, because the same player at your next pick is a ~5% shot.

Real leaguemates are less rational than ADP bots. Value falls further than the model predicts, so when a tier-3 player is somehow there two rounds late, take him.

## 7. Tiers and cliffs

Tiers are groups of players close enough in projection that which one you get barely matters. Build them from projection gaps, not from rounds and not from ADP. Rules:

- Sort the position by projection. Start a new tier wherever the gap to the next player is meaningfully larger than the gaps inside the group: at least 8 points *and* more than 1.5× the median of the neighboring gaps. Never split on a gap under 6 points — the flat middle of the WR and RB rankings has dozens of 3-point gaps, and splitting there produces tiers that mean nothing.
- Label the cliff with the point drop. Cliffs are where paying up or deliberately waiting matters; inside a tier, take the scarcer position or the safer role.
- Note where a tier spans many rounds of ADP. That is the market mispricing the position and it is where your surplus comes from.
- Draft across tiers, never within them: if two players are in the same tier at your pick, the tiebreak is position scarcity, then role certainty, then the higher There % at your next pick (take the one who won't be there).

## 8. Scarcity by position: what usually holds, and how scoring bends it

Patterns that recur most seasons, to be verified against this year's data rather than assumed:

- **RB** has a cliff where bell-cow roles end and committees begin, then a long dead zone of camp battles and timeshares. Two flex spots and 14 teams strip the dead zone before ADP says they will.
- **WR** is deep and forgiving in the middle rounds; a dozen receivers within 15 points of each other from ADP 45 to 75 is common. That depth is exactly why not to spend early picks there unless the scoring is full PPR with three WR slots.
- **TE** is barbell-shaped: one to three elite options with a two-round edge on the field, then a long usable middle. Pay at the top or wait; never pay in between.
- **QB** is the deepest position in 1QB leagues, and 4-point passing TDs with an interception penalty compress QB1-to-QB8 to under two points a week. The correct QB round is usually 7 or later. Superflex inverts this entirely.
- **K/DEF** are near-interchangeable; the spread between the best and the fifteenth is small and unpredictable. Final two rounds.

Scoring bends all of this: full PPR lifts pass-catching backs and slot receivers; 6-point passing TDs pull QBs up two rounds; TE premium (1.5 PPR for TEs) makes the second TE tier startable at flex; big-play bonuses favor deep threats. Re-derive replacement levels rather than remembering last year's conclusions.

## 9. Reach rules

A reach is paying a pick earlier than a player's realistic availability. It is earned by one thing: **role certainty in a tier that's about to run out**. It is never earned by upside in the first three rounds — those picks must be weekly starters with a locked role.

- Cap any reach at one round.
- Never reach for a player whose There % at your next pick is above ~80%; you're paying for something you'd get free.
- The endorsed reach is usually a bell-cow-shaped back sitting in the dead zone at the price of a committee back.
- Before reaching, check the injury feed for that player from the last 72 hours. Reaching for a player who missed practice Wednesday is how seasons are lost.

## 10. Building projections you can defend

Start from a consensus stat line (targets, receptions, yards, touchdowns, attempts) — consensus is a better median than any single source. Then adjust, with a written reason each time, for:

- Role changes with evidence: a coordinator quote, a trade, draft capital spent, a depth-chart move, a camp report from a beat reporter.
- Expected games played, as an injury discount. Don't model injury separately; bake it into expected games.
- Regression toward career norms on efficiency stats (yards per route run, touchdown rate) that came from small samples or unsustainable target shares.
- Team context: projected pass rate over expectation, pace, offensive line health, win total (winning run-first teams throw less).

Score the stat line in the league's exact settings. Never accept a vendor's point total when the scoring differs; a −2 INT, 4-point-TD league reorders the quarterbacks.

Write the three or four projections you most changed from consensus into the appendix with the reason. That's what makes the analysis yours and checkable.

## 11. Sample drafts and the target build

Run 8–10 full drafts (script or by hand). Report:

- The range of projected starter points across runs, and what it means per week. A 46-point spread across ten drafts is under three points a week — that's the message that the *structure* matters more than any single pick.
- The most-owned players across runs: these are the players the math keeps choosing, and they should headline the target list.
- What happened in every draft (e.g., "QB always waited", "no WR before pick 93 in seven of ten"). Those are the strategic conclusions.
- The single roster to aim for, every pick of which is realistically reachable (There % ≥ ~45%), its projected total, why it beats the others, and its known weakness with a concrete hedge ("Pittman at 93 instead costs 8 points and buys a real WR3").

Don't present the top-scoring draft as the plan if it depends on a 34%-likely fall. Present it as the upside case.

## 12. Late rounds: handcuffs and next-year keepers

In deep leagues the waiver wire is close to empty by October, so:

- The backup to each of your own starting backs is defensive value, not a luxury.
- Second-year players with a path to volume beat veterans with a known, capped role.
- In keeper leagues where waiver pickups can't be kept, a breakout drafted in round 11 becomes a round-11 (or round-10) keeper next season — the only cheap keeper you can manufacture. Bias the last four rounds hard toward that.
- K and DEF in the final two rounds. Streaming defenses by matchup beats drafting one early in almost every scoring system.

## 13. Superflex, 2QB, TE-premium, best ball, auction

- **Superflex / 2QB**: treat the flex as a QB starter when computing replacement. QBs become the scarcest position; take two in the first five rounds in most 12-team superflex formats; a QB keeper is almost always the keep.
- **TE premium**: recompute TE replacement with the premium applied; the second tier becomes flex-worthy and the elite tier gains a round of value.
- **Best ball**: no waivers, no lineup decisions — draft for weekly ceiling and stacking; late-round upside matters more, handcuffs matter less. Replacement level is lower because you start your best scores automatically.
- **Auction**: convert surplus to dollars. Total league budget minus $1 per bench slot gives the money that buys starters; each player's share of total starter surplus times that pool is his fair price. Keeper leagues in auction formats price keepers at last year's cost versus this year's fair price. The rest of the reasoning (tiers, cliffs, scarcity) is unchanged.

## 14. Sensitivity: the assumption that flips the board

Every analysis ends with the one estimate everything else depends on. Usually it is the RB-versus-WR replacement gap: if receiver projections are systematically 8–10% low, the correct pick at your early turns shifts toward WR. Name the assumption, say what changes if it's wrong, and tell the user to disagree with it *before* the draft rather than during.

Other common flip assumptions: a keeper's eligibility, a superflex slot the user forgot to mention, an injury designation announced draft morning, and the platform's default rankings pulling a QB up a round.

## 15. Signal versus noise in the room

What moves the needle: role (route share, snap share, touch share), earned volume (targets per route run, target share), the team's pass volume and pace, capital committed to the player, red-zone share, and expected games played. What doesn't, or barely: preseason box scores, a single big game, "hype", yards per route run on fewer than ~250 routes, and last year's touchdown total. `references/metrics.md` gives the ranking with the reasoning.

The market is smart about the top of the board and lazy about the middle. Your edge lives in the middle — the dead zone, the tier that spans four rounds, the platform-specific mispricing — and in the two or three checks nobody else made.
