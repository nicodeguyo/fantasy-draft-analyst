# Methodology — how a league-winner thinks at the draft table

This is the reasoning behind every recommendation the skill makes. It's written so you can explain each decision to a novice in one sentence and defend it to a data scientist in three.

Contents

1. The three ideas that do all the work
2. Pick value by rollout: simulating the rest of the draft
3. Replacement level and surplus: what they explain, and what they no longer decide
4. Keeper math: cost, market value, inflation, and the flip conditions
5. Pick geometry: snake picks, turns, and what keepers do to the board
6. Availability: Monte Carlo, and the pencil-and-paper shortcut
7. Tiers and cliffs
8. Scarcity by position: what usually holds, and how scoring bends it
9. Reach rules
10. Building projections you can defend
11. Cost of waiting, sample drafts, and the target build
12. Late rounds: handcuffs and next-year keepers
13. Superflex, 2QB, TE-premium, best ball, auction
14. Sensitivity: the assumption that flips the board
15. Signal versus noise in the room

---

## 1. The three ideas that do all the work

**The lineup, not the player.** A pick is not a purchase, it's a branch. What you want to know on the clock is which of the players in front of you leaves you with the best starting lineup in January — after the rest of the draft happens. That is a question you can answer by playing the rest of the draft out, many times, once for each candidate, and looking at the lineups. It needs no theory of what a player is "worth" and no parameter you have to guess. §2 is how.

**Price the market you're in.** ADP tells you what a generic drafter pays. Your league is not generic: it has this platform's default rankings pulling on the room, this many teams, these keepers already gone, and these specific humans with their specific habits. A player's "value" is what he costs *here*, at *your* picks. Keeper removals alone can shift the effective board by half a round or more.

**Say the bear case out loud.** Every verdict comes with the strongest argument against it and the one fact that would change it. This is not hedging — it's how you avoid the season-losing mistake, which is almost always a confident pick made without checking the thing that was checkable.

## 2. Pick value by rollout: simulating the rest of the draft

At every pick you are choosing between four or five plausible players. The honest question is not
"who is worth more" in the abstract — it is **which of them leaves me with the best starting lineup
once this draft finishes**. That question has a direct answer, and the answer needs no baseline.

The method, per pick *p* and candidate *c*:

```
1. Draft from the start to pick p — keepers removed, the other teams drafting off ADP with noise,
   and you taking your plan targets at your earlier picks (the heuristic policy when a target is gone).
2. If c isn't on the board at p in this sample, this sample can't say anything about him. Skip it.
3. Take c. Draft the rest of the way out: you on the heuristic policy, the room on ADP as before.
4. Score your best legal starting lineup.
5. pick_value(p, c) = the average of step 4 over the samples where c was there.
```

Rank the candidates at *p* by that number. The top one is the plan target, the second is Plan B, and
the plan path moves on with the target on your roster.

Three details make the numbers mean something:

**Common random numbers.** Draw each sample's draft *once* up to pick *p* and branch that same state
for every candidate. Every candidate then faces the same room doing the same things, so the
differences between them are about the players and not about which sample they happened to land in.
It is also what makes the whole thing affordable: the prefix is carried forward from one of your
picks to the next, so a sample's draft is played once, not once per pick and not once per candidate.

**A matched control arm.** A candidate is only scored on the drafts where he was actually available —
and a player who falls to you one time in five only falls in the drafts where *the whole board* fell.
Compare raw averages and he looks like a genius for something that had nothing to do with him. So each
sample is also played out with nobody forced in, and a candidate is measured by the **difference** he
makes on his own samples. The luck of the board sits in both terms and cancels. What's reported is
that difference added back to the control average, so the number still reads as a projected lineup.

**Noise.** Every value comes with a standard error. Two candidates inside about two standard errors of
each other are not distinguishable — say so ("level with"), and break the tie on scarcity, role
certainty, or who is less likely to be there next time. Reporting a 1.4-point edge as a decision is
how a simulation starts lying to you.

**What the number is, and what it is not.** A pick value is the projected lineup *at that pick*,
measured against a control arm — the same drafts played out with nobody forced in — on the same
samples. That makes candidates at one pick exactly comparable with each other, which is the
comparison the board asks you to make. It does **not** make picks comparable with each other. Each
pick's control arm already assumes you followed the plan to get there, so the column drifts downward
as the draft goes on; a 1,858 at pick 5 and a 1,842 at pick 101 are not a decline in your team, they
are two different baselines. `control` and `vs_control` are in the output so you can see it. Never
subtract one pick's value from another's, and never read a pick value against a keeper-scenario
total — those come from a free-running policy and sit on a different scale again.

**One more honest limit, and it is the one to argue with.** Simulate a drafter who follows the plan
and you get 1,839 on the sample league. Simulate the same drafter choosing freshly at every pick with
the heuristic policy and you get 1,863 — 24 points better, a point and a half a week. The tool's own
recommendation trails the tool's own default. Two things are going on and only one of them is benign:

* A plan is a ranking computed *before* the draft. Someone reacting to the actual board can always do
  a little better, and no written plan can capture that. That part is the price of having a plan at
  all, and the board recovers most of it by being adaptive: it shows the whole ranked list and tells
  you to take the top row *still on the board*, which is the policy those 1,839 points already
  assume.
* The rest-of-draft policy inside a rollout is the same heuristic. When a rollout forces in a player
  that heuristic would not have taken, the heuristic then has to repair a roster shape it did not
  plan, and it repairs imperfectly. So a candidate is charged for the policy's rigidity as well as
  for his own merits. That is a real bias against exactly the picks where the rollouts disagree most
  interestingly with the heuristic — and it is the first thing to fix in a v2.1.

What survives both: the *ranking* and the *gaps* within a pick, which is all the board asks you to
read. What does not: treating the plan's projected lineup as a promise, or as better than what a
sharp drafter would have done anyway.

Reading the output: `pick_values[p]` is the ranked list with `value`, `vs_control`, `control`,
`delta_vs_best` (the board's **Now** column), `se`, `n`, `avail_pct` and `next_pct`; `plan_path` is the greedy path with its Plan B
and its "if he falls" upside. A plan target has to be someone you can realistically expect to be
there — the default floor is 50%. A better player available one draft in five is *upside*, not a plan,
and belongs in the row as "Bijan if he falls (21%)".

What the rollouts do **not** remove: the rest-of-draft policy is still the lineup-aware heuristic, and
that heuristic uses surplus internally. That is fine, and it is worth being clear about why. The
policy is a stand-in for "you draft sensibly from here"; the *evaluation* is the final lineup, which
is a fact about the roster and involves no baseline at all. A mediocre policy makes every candidate
look similar (it shrinks the differences); a biased baseline inside the policy cannot make a bad
lineup score well. The decision no longer depends on the parameter that used to decide it.

## 3. Replacement level and surplus: what they explain, and what they no longer decide

Replacement level at a position is the projected total of the worst player who still has to be in
someone's starting lineup every week. **Surplus** is a player's projection minus that number. Together
they are the clearest one-glance answer to "which positions are deep this year" — which is why they
are still the tier boards' column and still the thing to quote when explaining why a 215-point
receiver can be a worse pick than a 203-point back. They are no longer what ranks a pick.

Compute it by **flex equilibrium**, which is how lineups actually get filled:

```
1. Fill the dedicated slots: teams × slots at each position (the 28 best RBs in a 14-team, 2-RB league).
2. Pool everyone left at the flex-eligible positions (RB/WR/TE) and give every flex slot league-wide
   to the best remaining player, regardless of position.
3. Add a few "virtual" flex slots for byes and injuries (2 in a 10-team league, 3 in 12, 4 in 14).
4. replacement[pos] = projection of the last player at that position who got a slot.
```

The marginal RB and the marginal WR end up worth about the same — in a 14-team, two-flex league with
this year's pool, RB38 ≈ 132 and WR50 ≈ 130, with the 32 flex-and-pad slots filling 10 RB / 22 WR
because the receiver pool is deeper. Superflex/OP slots are filled by QBs ~85% of the time; treat them
as 0.85 of an extra QB starter. Read the flex fill the simulator reports (`flex_fill`) — it tells you
which position the league's depth actually lives in.

**Why this stopped being the decision.** Replacement level is an estimate, and this year it lands on a
cliff in the running-back projections: RB37 projects 132 and RB40 projects 111. Move the baseline
three ranks — which is well inside honest disagreement — and every back on the board gains or loses
twenty points of surplus at once. Two defensible ways of drawing the line produced opposite plans for
the same league: one drafted eight running backs, the other took receivers in rounds 2 and 3. Nothing
about the players changed. That is the signature of a decision resting on a parameter rather than on
evidence, and it is why v2 measures lineups instead. The fixed-share model that caused the worse of
those two plans (`roster.flex_mode: fixed_share`) is still available for a league you know flexes
irrationally, and `replacement_rank` overrides any position outright — but neither moves the pick
tables now, only the tiers' column and the appendix.

Never rank a decision by "picks of value" (ADP minus cost) either. Points-per-pick is steepest at the
top of the board: the gap between WR3 and WR12 overall is far larger than the gap between RB25 and
RB35. A keeper who saves you four picks on a top-5 player is worth more than one who saves you twenty
picks in round 8. Translate every "he's a steal" claim into points before you believe it.

Deeper leagues push replacement down at every position and make scarce positions scarcer; that is why
the same player is a round more valuable in a 14-team league than a 10-team league. Scoring bends it:
full PPR lifts pass-catching backs and slot receivers; TE premium moves the second TE tier into flex
territory; 6-point passing TDs pull QBs up.


## 4. Keeper math

For each candidate:

1. **Cost** — the pick number the keeper consumes. Convert the keeper's round to the user's overall pick in that round (snake order). Round-minus-one rules mean a player drafted in round 3 costs the round-2 pick; check `references/keeper-rules.md` for the taxonomy.
2. **Market value** — the player's current ADP on the user's platform, expressed as an overall pick.
3. **Inflation adjustment** — with K keepers removed from the pool before the draft, the player actually on the board at pick p is worse than ADP p suggests. How much worse depends on whether keepers *cost picks*:
   - In leagues where each keeper consumes that team's pick in the keeper's round (same-round, round-minus-one, and similar), inflation is **front-loaded**: keepers are mostly top-60 players, so the top of the board is thinned, but every forfeited pick puts a player back. Net inflation at pick p ≈ (keepers already "ahead" of p) − (forfeited picks before p). Measured by simulation in a 12-team one-keeper league: about +11 at pick 5, +8 at pick 20, +6 at 29, +4 at 44, and roughly zero from round 6 on. So pick 20 delivers the ADP-28 player, and a round-6 pick delivers a true round-6 player.
   - In leagues where keepers are free (no pick forfeited — a fixed last-round cost, or an extra roster slot), inflation is close to K at every pick and doesn't fade.
   - `draft_sim.py` measures the inflation actually in force at each of your picks (`inflation_at_pick`); quote that rather than a rule of thumb whenever you have it.
   - The consequence for keeper valuation: a keeper who costs an early pick is competing against an inflated board (his surplus is a little better than the raw pick-vs-ADP comparison shows); a keeper who costs a mid-round pick is competing against an almost un-inflated board (the raw comparison is about right).
4. **Surplus in points** — projection of the keeper minus projection of the player you'd realistically get with that pick after inflation. This is the number that *explains* the verdict.

The number that *decides* it is the same one the pick tables use: run the whole draft under each scenario — keep X, keep Y, keep nobody — and compare the mean projected final starting lineup (`--keeper-scenarios`, which writes `keeper_scenarios` to `sim.json`). That puts the keeper call in the same units as every other decision on the board, and it prices the thing the isolated surplus table can't: the pick you forfeit, the inflation it creates, and what the rest of your draft looks like without him. Lead with those totals and their standard errors ("keep JSN 1,914 · keep Warren 1,908 · nobody 1,904"), then show the surplus table underneath as the explanation. When two scenarios sit inside two standard errors of each other, the honest verdict is "close" — say it, and let the tiebreak be the bear case rather than the third decimal.

Then run the flip checks:

- **Eligibility.** Waiver pickups, traded players, or players kept last year may be ineligible or priced differently. This is the single most common "the whole analysis changes" fact; ask before you compute.
- **Superflex / 2QB.** A QB keeper's surplus roughly doubles because the replacement QB drops from the 12th-best to the 24th-best. Josh Allen at a round-2 cost is a fade in 1QB and an easy keep in superflex.
- **Escalation.** If a kept player's cost rises a round each year, a round-1 keeper has nowhere to go and the "keep him again next year" option is worthless — a mild argument for taking value elsewhere, rarely enough to change this season's call.
- **Keeping nobody.** Always price it. It's usually dominated — you forfeit surplus for nothing — but if every candidate is negative, keeping nobody and drafting the round is correct.
- **Next-year optionality.** A cheap late-round keeper that you can hold for years is worth more than its one-season surplus. Note it; don't let it override a large one-season gap.

Present the scenario totals first, then the table: Player | Cost (round → pick) | ADP | Surplus in picks | Surplus in points | Verdict. Then the verdict paragraph, the bear case on the chosen keeper, and "the one thing to confirm."

## 5. Pick geometry

Snake draft, T teams, slot s: round r pick is `(r−1)×T + s` when r is odd and `r×T − s + 1` when r is even. Slot 11 of 14: 11, 18, 39, 46, 67, 74, 95, 102, 123, 130, …

Two things to read off the ladder:

- **Turn tightness.** Slots at the ends have paired picks (1 and 28 in a 14-team league; 14 and 15). Middle slots have evenly spaced picks (~14 apart). Paired picks let you plan two-player combinations ("RB + RB at 33/40"); evenly spaced picks mean you cannot count on anyone surviving a full round.
- **Keeper forfeits.** Each team loses the round its keeper cost. Remove those picks from the order. The user's own forfeited round shifts nothing for them but changes what's on the board for everyone else — the sim handles this; by hand, just note that K picks are missing.

`references/draft-slot-playbook.md` walks through early, middle, and late slots by league size.

## 6. Availability: Monte Carlo, and the pencil-and-paper shortcut

**With the script.** `draft_sim.py` removes keepers (weighted toward better players, with keeper rounds correlated to player quality — or the league's published list if you have it), then drafts the other teams on ADP plus noise scaled to each player's observed ADP spread (capped, so deep sleepers aren't drafted in round 5), with a positional-need bias from round 8 on and a realistic K/DEF curve, and records who is on the board at each of the user's picks across 1,500 runs. "There %" is that frequency. Below 50%: plan for him being gone. Above 80%: no reason to reach. The script always reports the user's own players and "my guys" at every pick, and writes a full name × pick availability matrix (`sim_availability.csv`) for anyone else you need to look up.

The "you" in the availability pass drafts off ADP like everyone else, on purpose: "will he still be there at my next pick" has to be a fact about the other managers, not about whether your own plan already took him. Inside the rollouts (§2) the simulated you drafts by the lineup-aware heuristic — surplus, adjusted for lineup need and for the opportunity cost of waiting — because there it is a stand-in for you drafting sensibly, not the thing being measured.

**Without the script.** Availability at pick p for a player with ADP a and spread σ is approximately `P(available) = 1 − Φ((p_eff − a)/σ_eff)` where Φ is the standard normal CDF, `p_eff = p + inflation at that pick` (from §4), and `σ_eff = max(σ, 4) + 0.15 × inflation` to reflect keeper uncertainty. Quick table for `(p − a_eff)/σ_eff`: −2 → 98%, −1 → 84%, 0 → 50%, +1 → 16%, +2 → 2%. A player with ADP 49, σ 5, at pick 44 with +4 inflation (p_eff 48): z = (48 − 49)/5.6 ≈ −0.2 → ~57% available. A coin flip — take him now if he's the target, because the same player at your next pick is a ~5% shot.

**Deciding without the script: dynamic VBD.** You can't roll out a hundred drafts by hand, but you can do the same idea one pick ahead, which is most of the value. A player's take-now value is his projection minus the projection of the best player *at his own position* you expect to still be there at your next pick:

```
take_now(player) = projection − E[best same-position projection at your next pick]
```

Estimate that expectation with the availability shortcut above: walk down the position list and take the first player whose availability at your next pick is comfortably over 50%. Then filter by your lineup: a player who would not start for you, at a position where your slots are already filled, is worth roughly nothing this pick no matter how the arithmetic looks.

Why this beats plain surplus in a chat-only setting: it is a *difference between two things that will actually be on your board*, not a difference against an assumed league-wide baseline. Two candidates at different positions get compared on what each one costs you to pass up, which is the question the rollouts answer properly. It is the same idea, one pick ahead, by hand.

Its limits, stated honestly: it looks one turn forward instead of to the end of the draft, so it undervalues the second and third player at a position that is about to collapse, and it can't see roster interactions past the next pick. Where code execution is available, the scripted rollouts are strictly more accurate and should be used — say which method produced the numbers.

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

## 11. Cost of waiting, sample drafts, and the target build

**Cost of waiting** answers "when do I take which position" with numbers instead of a slogan, and it
is the one position-timing view the replacement-level argument cannot touch. For each of your picks
and each position, it is the drop between what is expected to be on the board now and what is expected
to be there at your *next* turn:

```
cost_of_waiting[pick][pos] = E[best surplus available at this pick]
                           − E[best surplus available at your next pick]
```

Both terms carry the same replacement level, so it cancels. That is not a hand-wave — it's measured.
Override `roster.replacement_rank` for RB by ±20 ranks in the sample league (moving the RB baseline
from 164 points to 92 and to 229) and the RB cost-of-waiting cells move by at most 4 points, all of it
second-order noise from the simulated you drafting slightly differently. The same override moves the
*surplus levels* those cells are built from by up to 73 points. That gap is the whole argument for
showing one on the board and not the other. Read it as: the outlined cell in each row is the position about to
run out, and the number is what one more turn of waiting costs you in points.

A typical 12-team reading: "waiting on a back costs 47 points at your first pick and almost nothing at
your third; tight end has a 22-point window at 20 and another at 53; quarterback never costs more than
six until round 5, so it can wait." In a superflex league the QB column dominates the early rows; in TE
premium the TE column does. The table changes with the league, which is why the skill never hard-codes
"RB early" or "WR late."

Two rules for reading it: (1) the lineup must still get filled — you take a second RB by the last pick
where waiting on one still costs you something, even if WR costs more there; (2) a position whose row
cells are all small (QB, usually) can wait until the last of those picks. And note what it is *not*:
cost of waiting says which position is draining, `pick_values` says who to take. When they disagree,
the rollouts win — they are the ones that measured a lineup.

**Sample drafts.** Run 8–10 full drafts (script or by hand), with the plan path in place so they show
what following the plan actually produces. Report:

- The range of projected starter points across runs, and what it means per week. A 46-point spread across ten drafts is under three points a week — that's the message that the *structure* matters more than any single pick.
- The most-owned players across runs: these are the players the math keeps choosing, and they should headline the target list.
- What happened in every draft (e.g., "QB always waited", "no WR before pick 93 in seven of ten"). Those are the strategic conclusions.
- The single roster to aim for — which is `plan_path` — its projected lineup, why it beats the alternatives at each step, and its known weakness with a concrete hedge ("Pittman at 93 instead costs 8 points and buys a real WR3").

Don't present the top-scoring draft as the plan if it depends on a 34%-likely fall. Present it as the upside case.


## 12. Late rounds: handcuffs and next-year keepers

In deep leagues the waiver wire is close to empty by October, so:

- The backup to each of your own starting backs is defensive value, not a luxury.
- Second-year players with a path to volume beat veterans with a known, capped role.
- In keeper leagues where waiver pickups can't be kept, a breakout drafted in round 11 becomes a round-11 (or round-10) keeper next season — the only cheap keeper you can manufacture. Bias the last four rounds hard toward that.
- K and DEF in the final two rounds. Streaming defenses by matchup beats drafting one early in almost every scoring system.

## 13. Superflex, 2QB, TE-premium, best ball, auction

- **Superflex / 2QB**: treat the flex as a QB starter when computing replacement. QBs become the scarcest position; take two in the first five rounds in most 12-team superflex formats; a QB keeper is almost always the keep.
- **TE premium**: the premium has to be in `players.csv` — `scoring.py` applies it when it scores stat lines, and the simulator will say so if `scoring.te_premium` is set. Once it is in the projections, TE replacement recomputes on its own, the second tier becomes flex-worthy and the elite tier gains value. Be aware the effect is smaller than it looks: points and receptions scale together at tight end, so a per-reception premium lifts the whole pool nearly proportionally and moves replacement almost as much as it moves the elite.
- **Best ball**: no waivers, no lineup decisions — draft for weekly ceiling and stacking; late-round upside matters more, handcuffs matter less. Replacement level is lower because you start your best scores automatically.
- **Auction**: `draft_sim.py` stops on `draft_type: auction` rather than pretending — it drafts picks, not dollars. Convert surplus to dollars by hand. Total league budget minus $1 per bench slot gives the money that buys starters; each player's share of total starter surplus times that pool is his fair price. Keeper leagues in auction formats price keepers at last year's cost versus this year's fair price. The rest of the reasoning (tiers, cliffs, scarcity) is unchanged.

## 14. Sensitivity: the assumption that flips the board

Every analysis ends with the one estimate everything else depends on. It used to be the RB-versus-WR replacement gap; measuring lineups instead of levels took that one off the table, and what is left is more honest and more interesting: **the projections themselves**. If receiver projections are systematically 8–10% low, the rollouts will happily build you the wrong roster, because they take the projections as given. Name the two or three projections the plan leans on hardest, say what changes if they're wrong, and tell the user to disagree with them *before* the draft rather than during.

Other common flip assumptions: a keeper's eligibility, a superflex slot the user forgot to mention, an injury designation announced draft morning, and the platform's default rankings pulling a QB up a round.

## 15. Signal versus noise in the room

What moves the needle: role (route share, snap share, touch share), earned volume (targets per route run, target share), the team's pass volume and pace, capital committed to the player, red-zone share, and expected games played. What doesn't, or barely: preseason box scores, a single big game, "hype", yards per route run on fewer than ~250 routes, and last year's touchdown total. `references/metrics.md` gives the ranking with the reasoning.

The market is smart about the top of the board and lazy about the middle. Your edge lives in the middle — the dead zone, the tier that spans four rounds, the platform-specific mispricing — and in the two or three checks nobody else made.
