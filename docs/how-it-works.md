# How it works — the data science behind the draft board

This is the explainer for anyone who wants to know *why* the skill says what it says: what moves the needle, what's noise, and where the edge actually comes from. Nothing here requires code. The formulas are the ones the scripts use.

## 1. The draft is a market, and most people mis-price it in the same direction

Every fantasy draft has the same shape. Everyone has a ranking (usually their platform's default), everyone drafts roughly in that order with some noise, and the winners are the people who understood two things the ranking doesn't show: **what a player is worth relative to the alternative** and **what a player will actually cost in this room**.

The skill is built to compute those two things well, then to be honest about what it doesn't know.

## 2. Replacement level: the number that decides the draft

Suppose your league has 12 teams that each start 2 RB, 2 WR, and a flex. Every week, roughly 24 + 7 = 31 running backs and 24 + 5 = 29 receivers are in someone's lineup (the flex splits about 55/40 between RB and WR in half-PPR). Add a few for byes and injuries and you get: the 34th-best running back and the 32nd-best receiver are the worst players anyone *has to* start. Their projected totals are the **replacement level** at each position.

In the example league those numbers are 137 (RB) and 165 (WR). That 28-point gap is the whole draft:

```
surplus = projection − replacement[position]

Zay Flowers  (WR)  215 − 165 = +50
Breece Hall  (RB)  203 − 137 = +66
```

Flowers projects twelve points *more* than Hall and is the *worse* pick, because the receiver you can get for free is much better than the back you can get for free. Every board in the skill is ranked by surplus, never by projection.

Why this is the right frame and not just a clever one: your final score is the sum of your starters. Drafting a player only changes that sum by the difference between him and whoever would have filled that slot. Everything else is noise. Replacement level makes the "whoever" explicit.

Scoring bends it. Four-point passing touchdowns with −2 per interception compress the difference between QB1 and QB8 to under two points a week, which is why the correct quarterback round is usually seven or later. Full PPR lifts pass-catching backs. TE-premium makes the second tight-end tier startable. A superflex slot roughly doubles the number of quarterbacks started league-wide and makes QB the scarcest position. The skill re-derives replacement level from *your* lineup and scoring rather than remembering last year's conclusion.

## 3. Points, not picks

"He's a round-3 value in round 6" is the most common way keepers get evaluated, and it's wrong more often than it's right. Points per pick are steepest at the top of the board: the gap between the third and twelfth receiver is far bigger than the gap between the 25th and 35th back. So a keeper who saves you four picks on a top-five player can be worth more than one who saves you twenty picks in round eight.

The skill measures keeper surplus in points: the keeper's surplus minus the surplus of the player realistically available with the pick he costs. In the example, two keepers showed the same "+14 picks" of value — a QB costing pick 77 and a WR costing pick 92 — and were worth 0 and −26 points respectively; the keeper that was actually worth +54 points was a running back costing pick 68, because points-per-pick is steepest at the top and the 68th and 92nd picks are different currencies.

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

## 6. Price the room you're in

ADP is not one number. It is the average of the drafters who produced it, and drafters follow their platform's default rankings. In the 2026 cross-platform data:

- **ESPN** rooms take elite QBs and TEs a round-plus early (Josh Allen ~17 on ESPN vs ~38 on Underdog; Bowers 26 vs 41 in mocks) and let receivers slide 10–17 picks.
- **Sleeper** is a barbell: the top two or three QBs go very early, everyone else very late, and running backs slide (a younger, Zero-RB-leaning user base).
- **Yahoo** tracks its own sharp default ranks; QB1s go early, receivers get pushed down, tight ends have historically been undervalued.
- **Underdog** (best ball, no waivers) inflates late-round ADP and moves fast on camp hype.
- **Mock-draft ADP** (FantasyFootballCalculator) is the format baseline and the source of the spread, but it's produced by mock drafters with more autopicks and less roster discipline than real leagues.

In the example run, repricing the same player pool from mock ADP to ESPN ADP moved Trey McBride's availability at pick 29 from 80% to 15%, Kyle Pitts at 77 from 88% to 16%, and Zay Flowers at 29 from 18% to 85%. Same players, same projections, different room, different plan.

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

Ten simulated drafts from your slot usually land within about 45 points of each other — under three points a week. That's the message: **structure matters more than any single mid-round name.** The skill reports the range, what happened in essentially every draft ("QB always waited"), the players the math kept choosing, and one roster to aim for in which every pick is realistically reachable. It does not present a build that depends on a 30%-likely fall as the plan; that's the upside case.

## 10. The assumption that flips the board

Every analysis ends with the estimate everything else depends on. It is usually the RB-versus-WR replacement gap: if receiver projections are systematically 8–10% low, the correct pick at your early turns shifts toward WR. Other common flips: a keeper's eligibility, a superflex slot the user forgot to mention, an injury designation announced draft morning, and the platform's default rankings pulling a quarterback up a round.

Naming that assumption is the difference between a model you can argue with and a hot take.

## 11. What this doesn't do

It doesn't know your leaguemates, though you can tell it about them. It doesn't have paywalled route-share data for the current preseason; it works from what's free and quotes sample sizes. It doesn't remove variance from football. What it does is make every decision explicit, sourced, and dated — so that when you disagree, you can disagree with a specific number.
