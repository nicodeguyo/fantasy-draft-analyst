# How it works — the data science behind the draft board

This is the explainer for anyone who wants to know *why* the skill says what it says: what moves the needle, what's noise, and where the edge actually comes from. Nothing here requires code. The formulas are the ones the scripts use.

## 1. The draft is a market, and most people mis-price it in the same direction

Every fantasy draft has the same shape. Everyone has a ranking (usually their platform's default), everyone drafts roughly in that order with some noise, and the winners are the people who understood two things the ranking doesn't show: **which available player leaves them with the best team when the draft ends** and **what a player will actually cost in this room**.

The skill is built to compute those two things well, then to be honest about what it doesn't know.

## 2. Ask the question you actually have: simulate the rest of the draft

You are on the clock. Four names are plausible. What you want to know is not which of them is "worth more" in the abstract — it is which one leaves you with the best starting lineup in January, after the other eleven managers have taken another hundred players.

That is a question you can answer directly, and it's a strange thing that most tools don't:

```
For each candidate at your pick:
  1. Play the draft up to your pick — keepers gone, everyone else drafting off ADP with noise.
  2. Put this candidate on your roster.
  3. Play the rest of the draft out.
  4. Add up your best legal starting lineup.
Do that 200 times. The average is that player's PICK VALUE.
```

The board shows the difference between the best candidate and each of the others. Take Brock Bowers at pick 20 and your projected lineup is 1,859. Take Nico Collins instead and it's 1,845. That "−14" is the whole message: fourteen points across a season, under one a week, is a real but small cost — and knowing it's small is as useful as knowing which one is bigger.

Three details keep the numbers honest.

**Every candidate faces the same draft.** The draft up to your pick is played *once* per simulation and then branched — the same keepers gone, the same managers making the same reaches. So the differences between candidates are about the players and not about which simulation each happened to land in.

**A player is only judged against what you'd have done otherwise.** A stud who falls to you one time in five only falls in the drafts where the *whole board* fell — the ones where you were going to do well anyway. Compare raw averages and he gets credit for the good luck that delivered him. So every simulation is also played out with nobody forced in, and each candidate is scored on the *difference* he makes in his own simulations. The luck sits in both numbers and cancels.

**Noise is reported, not hidden.** Every value comes with a standard error, and two candidates within about two of them are simply level. The board says "best" on both rows rather than inventing a 1.4-point winner.

## 2b. Replacement level: still useful, no longer in charge

The older idea — and the one almost every fantasy tool still runs on — is **value-based drafting**. Suppose your league has 12 teams that each start 2 RB, 2 WR, and a flex. Every week 24 running backs and 24 receivers start in dedicated slots, and 12 flex slots go to *whoever is better* among the backs, receivers, and tight ends left over. The last back and the last receiver to get a slot are the worst players anyone *has to* start. Their projected totals are the **replacement level**, and a player's **surplus** is his projection minus that:

```
surplus = projection − replacement[position]

Zay Flowers  (WR)  215 − 156 = +59
Breece Hall  (RB)  203 − 164 = +39
```

That is a genuinely good way to see *which pools are deep* — in the example league the flex-and-pad slots fill 4 RB / 11 WR, which tells you the receiver pool is the deeper one this year. It is still the column on the skill's tier boards.

**Here is why it stopped ranking the picks.** Replacement level is not measured, it's chosen — and this year the choice lands on a cliff. RB37 projects 132 and RB40 projects 111. Move the line three ranks, which is well inside honest disagreement between two careful analysts, and every running back on the board gains or loses twenty points of surplus at once.

That is not a hypothetical. Two defensible versions of this skill produced opposite plans for the same league from the same projections: v1.0 drafted eight running backs, v1.1 took receivers in rounds 2 and 3. Nothing about the players changed between them. When the answer moves that far on a parameter nobody can pin down, the parameter is doing the deciding — and the honest response is to stop needing it.

Simulated pick values need no such number anywhere. They compare final lineups, and a lineup total is a fact about a roster.

(The receipt for the earlier bug, since it's instructive: v1.0 assumed a fixed 55% share of flex slots for running backs, which in a 14-team league priced replacement at RB47 — 95 points — against WR43 at 143. It implied managers flex a 95-point back over a 143-point receiver, which nobody does. Computing the flex by *equilibrium* — every slot to the best remaining player — fixed that at the root and added about 35 points to projected starter totals. But it only moved the cliff; it didn't remove the dependence on where you draw the line. That took v2.)

Scoring bends all of it. Four-point passing touchdowns with −2 per interception compress the difference between QB1 and QB8 to under two points a week, which is why the correct quarterback round is usually seven or later. Full PPR lifts pass-catching backs. TE-premium makes the second tight-end tier startable. A superflex slot roughly doubles the number of quarterbacks started league-wide and makes QB the scarcest position — and the simulation finds that on its own, without being told, because an empty superflex slot is worth so little in the final lineup.

## 3. Points, not picks

"He's a round-3 value in round 6" is the most common way keepers get evaluated, and it's wrong more often than it's right. Points per pick are steepest at the top of the board: the gap between the third and twelfth receiver is far bigger than the gap between the 25th and 35th back. So a keeper who saves you four picks on a top-five player can be worth more than one who saves you twenty picks in round eight.

The skill measures keeper surplus in points: the keeper's surplus minus the surplus of the player realistically available with the pick he costs. In the example, two keepers showed the same "+14 picks" of value — a QB costing pick 77 and a WR costing pick 92 — and were worth 0 and −26 points respectively; the keeper actually worth keeping was a running back costing pick 68, because points-per-pick is steepest at the top and the 68th and 92nd picks are different currencies.

The verdict itself is now decided the same way the picks are: run the whole draft under each scenario — keep him, keep the other guy, keep nobody — and compare the mean projected starting lineup. In the example that reads 1,864 / 1,824 / 1,810, with standard errors under a point, which puts the keeper call in the same units as everything else on the board. The surplus table stays underneath as the explanation of *why* the gap is that size.

## 4. Keeper inflation is front-loaded (this surprised us)

With K keepers removed before the draft, the player available at any pick is worse than ADP implies. The folk rule is "add K to every pick." Measured in the simulator, it's more interesting than that.

When keepers **cost picks** (same-round and round-minus-one rules), two things happen at once: the best players leave the pool, *and* every team forfeits a pick in the keeper's round — which puts a player back on the board. The net effect at pick p is roughly (keepers already gone ahead of p) − (forfeited picks before p). Measured across 1,500 runs of a 12-team, one-keeper league:

| Your pick | 5 | 20 | 29 | 44 | 53 | 77 | 92 |
|---|---|---|---|---|---|---|---|
| Net inflation | +11 | +8 | +6 | +4 | +3 | +0.5 | 0 |

Pick 20 buys about the ADP-28 player; pick 77 buys the ADP-77 player. Two consequences: a keeper who costs an early pick is competing against an inflated board (slightly better than the raw math says), and a keeper who costs a mid-round pick is competing against an almost normal board — which is exactly why a round-6 keeper who became a first-round player is such a large edge.

When keepers are *free* (no pick forfeited), inflation is close to K everywhere and doesn't fade.

## 5. Availability is a probability

"Will he be there at 44?" has a number. The simulator draws the league's keepers (weighted toward better players, with keeper rounds correlated to quality — or uses the league's published list), then drafts the other teams on ADP plus noise scaled to each player's observed ADP spread, with a positional-need bias late and a realistic curve for when kickers and defenses go. 1,500 runs later, every player has a **There %** at each of your picks.

The rules that fall out of it:

- Below 50%: plan for him being gone.
- Above 80%: don't reach — you're paying for something you'd get free.
- Between two targets, take the one with the lower There % at your *next* pick.

Without the simulator, the same estimate comes from a normal distribution: `P(available) ≈ 1 − Φ((p_eff − ADP) / σ)`, with `p_eff` the pick plus the inflation above and σ the ADP spread (or `max(4, 0.08 × ADP)` if the source doesn't give one). It's cruder, and the skill says so when it uses it.

Real leaguemates are less rational than ADP bots. Value falls further than the model predicts, so when a tier-3 back is somehow there two rounds late, believe the board and take him.

## 5b. When to take which position — cost of waiting

"RB early, WR late" is advice for a league that may not be yours. The measured version asks a narrower question with a much better answer: **what does one more turn of waiting cost me at each position?**

```
cost_of_waiting[your pick][position] = best value expected on the board now
                                     − best value expected at your next pick
```

In the example 12-team league:

| Pick | QB | RB | WR | TE |
|---|---|---|---|---|
| 5 | 7 | **47** | 38 | 5 |
| 20 | 2 | 6 | 11 | **22** |
| 29 | 1 | 10 | **16** | 11 |
| 44 | 4 | **11** | 8 | 3 |
| 53 | 16 | 6 | 16 | **17** |
| 77 | 3 | **27** | 7 | 10 |

Read the bold cell in each row: that is the position about to run out. Waiting one turn on a back at pick 5 costs 47 points; by pick 44 it costs 11. Tight end has two windows, at 20 and again at 53. Quarterback never costs more than seven until round 5, which is the numerical version of "QB can wait."

The reason this table is trustworthy while the surplus *levels* it's built from are not: both terms carry the same replacement level, so it cancels. Shift the RB baseline by twenty ranks and every cell in the RB column stays exactly where it is. It is the one position-timing view the argument in §2b can't touch.

Change the league and the table changes: superflex puts QB on top, TE-premium puts TE there. And when cost of waiting and the pick values disagree, the pick values win — cost of waiting says which shelf is emptying, the rollouts say which player to take.

## 6. Price the room you're in

ADP is not one number. It is the average of the drafters who produced it, and drafters follow their platform's default rankings. In the 2026 cross-platform data:

- **ESPN** rooms take elite QBs and TEs a round-plus early (Josh Allen ~17 on ESPN vs ~38 on Underdog; Bowers 26 vs 41 in mocks) and let receivers slide 10–17 picks.
- **Sleeper** is a barbell: the top two or three QBs go very early, everyone else very late, and running backs slide (a younger, Zero-RB-leaning user base).
- **Yahoo** tracks its own sharp default ranks; QB1s go early, receivers get pushed down, tight ends have historically been undervalued.
- **Underdog** (best ball, no waivers) inflates late-round ADP and moves fast on camp hype.
- **Mock-draft ADP** (FantasyFootballCalculator) is the format baseline and the source of the spread, but it's produced by mock drafters with more autopicks and less roster discipline than real leagues.

In the example run, repricing the same player pool from mock ADP to ESPN ADP moved Trey McBride's availability at pick 29 from 80% to 15%, Kyle Pitts at 77 from 88% to 16%, and Zay Flowers at 29 from 18% to 83%. Same players, same projections, different room, different plan.

## 7. Signal versus noise in player evaluation

A projection is opportunity × efficiency × health. Opportunity is the stable part. The skill weights metrics in roughly this order, and the reasoning is the important part:

1. **Route share and snap share.** Opportunity precedes efficiency. Nearly every failed breakout call starts with someone extrapolating per-play numbers from a part-time player.
2. **Targets per route run and target share.** Earned volume, not just volume — paired with team pass attempts, because a high share of a low-volume passing game produces great rate stats and mediocre totals.
3. **Team pass rate, pace, total plays.** How many plays exist to be won.
4. **Capital committed** — draft picks and dollars are revealed preference about intended role.
5. **Red-zone share.** Touchdowns regress; the share of goal-line work regresses less.
6. **Coach quotes that name a number or a competitor.** "We'll get him the ball" is noise; "the split should be more equitable" is a committee.
7. **Yards per route run** — real, but unstable under ~250 routes. Use it to confirm a role story, not to create one.

Red flags the skill checks for: a breakout on a small sample; a surge that coincided with a teammate's injury, now healed; preseason box scores; an injury designation in the last week of camp; a tight end whose season total is dominated by one game.

**The betting market** is the best free consensus in sports. Win totals set the game-script prior (a high total on a run-first team caps its receivers). Season props are a sanity check on medians: if the book's yardage line implies fewer points than your projection, distrust your projection first. Season-long lines are softer than game lines and books under-price downside scenarios, which is why the unders are the historically exploitable side.

## 8. Reach rules

A reach is earned by exactly one thing: role certainty in a tier that's about to run out. Never by upside in the first three rounds — those picks must be weekly starters with locked roles. Cap any reach at one round. Never reach for a player who is 80%+ likely to be there at your next pick. And check the last 72 hours of news on him first; a player who missed Wednesday practice in draft week is a different pick.

## 9. Sample drafts and the target build

Ten simulated drafts from your slot usually land within about 45 points of each other — under three points a week. That's the message: **structure matters more than any single mid-round name.** The skill reports the range, what happened in essentially every draft ("QB always waited"), the players the math kept choosing, and one roster to aim for — the plan path, built pick by pick by taking the best pick value at each turn.

A plan target has to be someone you can realistically expect to be there; the floor is 50%. A better player who falls to you one draft in five is *upside*, not a plan, and the board says so in as many words: "Jaxon Smith-Njigba — Bijan Robinson if he falls (21%)." A build that depends on a 21% fall is not a build.

## 10. The assumption that flips the board

Every analysis ends with the estimate everything else depends on. It used to be the RB-versus-WR replacement gap; simulating lineups took that one off the table. What's left is more honest: **the projections themselves.** The rollouts take them as given, so if receiver projections are systematically 8–10% low, the simulation will cheerfully build you the wrong roster and report a tight standard error while doing it. Precision is not accuracy, and the skill says which one it is offering.

Other common flips: a keeper's eligibility, a superflex slot the user forgot to mention, an injury designation announced draft morning, and the platform's default rankings pulling a quarterback up a round.

Naming that assumption is the difference between a model you can argue with and a hot take.

## 11. What this doesn't do

It doesn't know your leaguemates, though you can tell it about them. It doesn't have paywalled route-share data for the current preseason; it works from what's free and quotes sample sizes. It doesn't remove variance from football. What it does is make every decision explicit, sourced, and dated — so that when you disagree, you can disagree with a specific number.
