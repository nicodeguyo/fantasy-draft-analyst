# Metrics — what predicts, what doesn't, and how to weight it

A fantasy projection is a bet on opportunity times efficiency times health. Opportunity is the most stable of the three, efficiency the least, health the hardest to know. Weight metrics accordingly, and treat every stat with a sample-size question attached.

Contents

1. The hierarchy (with why)
2. Position-specific notes
3. Stability table: what carries year to year
4. Using the betting market
5. Red flags and false signals
6. A pressure-test template for one player

---

## 1. The hierarchy

In rough order of predictive value for the coming season:

1. **Route share and snap share.** Opportunity precedes efficiency. Nearly every failed breakout call starts with someone extrapolating per-play numbers from a part-time player. A receiver on 45% of routes is not a starter no matter how efficient; a receiver on 85% of routes has a floor. Ask "what share of the offense's plays is he on the field for?" before any other question.
2. **Targets per route run (TPRR) and target share.** Earned volume, not just volume. TPRR above ~24% is elite; below ~17% is a decoy. Target share on a low-volume passing offense produces good rate stats and mediocre totals — always pair it with team pass attempts.
3. **Team pass rate over expectation, pace, and total plays.** How many plays exist to be won. A receiver on a team that led the league in attempts has a volume story that survives some inefficiency; a receiver on a run-first team with a high win total is fighting the game script.
4. **Capital committed.** What a team paid in draft picks or dollars is revealed preference about the intended role. A first-round pick or a $15M-per-year contract gets every chance; a fifth-rounder gets one bad game.
5. **Red-zone and goal-line share.** Where touchdown variance actually comes from. Touchdowns regress; the *share* of goal-line work regresses less.
6. **Coach and coordinator statements, weighted by specificity.** "We'll get him the ball" is noise. "He's our starter, and the split should be more equitable" is signal about a committee. Quotes that name a competitor or a number are the ones to trust.
7. **Yards per route run (YPRR).** Real, but the least stable of these on small samples. Below ~250 routes, YPRR is mostly noise; a 2.7 YPRR on 234 routes tells you far less than a 1.9 on 550. Use it to confirm a role story, not to create one.
8. **Age and experience curves.** Receivers peak around 25–28; backs decline sharply after age 27 or ~1,500 career touches; tight ends break out in year 2–3. Use as a prior, not a rule.
9. **Air yards and aDOT.** Useful for understanding the shape of a role (deep threat versus possession), less useful as a projection input on their own.

## 2. Position-specific notes

**Running backs.** The whole question is touches and the shape of the backfield. Bell-cow (70%+ of carries, most goal-line work, passing-down role) versus committee is a bigger determinant than talent. Check: the competitor's contract and health, the offensive line, expected game script (trailing teams throw to backs), and whether the coach has a history of one-back or two-back usage. Rookie backs with early-round capital behind a good line are the most reliable "breakout" archetype; a veteran on a one-year deal behind a rookie is the most common "dead" archetype.

**Wide receivers.** Route share first, then TPRR, then the quarterback. A receiver whose late-season surge coincided with a teammate's injury is a role bet, not a talent bet — ask what happens when the room is healthy. Slot versus outside matters in PPR (slot = more targets, fewer yards per catch). Receivers on new teams underperform ADP more often than not in year one.

**Tight ends.** Elite tight ends are elite because of route share on early downs plus red-zone usage. Everyone else is a touchdown lottery. A tight end who put up a third of his season in one game is not a top-five player; check the median week, not the total.

**Quarterbacks.** Rushing yards are the stable part (a designed-run QB has a floor); passing touchdowns are the noisy part. In 4-point-TD, −2-INT scoring, the difference between QB1 and QB8 is often under two points a week, which is why the correct round is late. Team pass attempts and offensive line matter more than arm talent.

**Kickers and defenses.** Near-random year to year beyond "good offense, plays in a dome" for kickers and "pass rush plus takeaways" for defenses. Don't spend analysis time here.

## 3. Stability table

Approximate year-over-year correlations for players with a stable role (use as intuition; exact values vary by source and era):

| Metric | Stability | Use it for |
|---|---|---|
| Snap share, route share | High | Floor and role |
| Target share | High | Volume projection |
| Targets per route run | Medium-high | Earned volume |
| Carries share (RB) | High | Volume projection |
| Yards per carry | Low | Almost nothing |
| Yards per route run | Medium (large samples), low (small) | Confirming a role story |
| Touchdowns | Low | Regression, both directions |
| Red-zone share | Medium | Touchdown expectation |
| Catch rate | Low-medium | Nothing on its own |
| Broken tackles / yards after contact per attempt | Medium | Talent tiebreak among similar roles |

Rule: when two metrics disagree, believe the more stable one.

## 4. Using the betting market

Sportsbooks are the best free consensus in sports, with one caveat: season-long props are softer than game lines and books tend to under-price downside scenarios (injury, benching), which is why unders are the historically exploitable side.

How to use them:

- **Win totals** set the game-script prior. A high total on a run-first team caps its receivers; a low total on a pass-heavy team lifts them (garbage-time volume is real). Note the juice: a total of 9.5 with the under at −140 is really about 9.
- **Player season props** (yards, touchdowns, receptions) are a sanity check on your median. If a book's yardage line implies fewer points than your projection, distrust your projection first. A receiving-yards line of 900.5 for a player being drafted in round 4 is the market telling you the ceiling is capped.
- **Awards and futures** (OPOY, rushing leader) are useful for identifying who the market thinks is the true No. 1 in an offense.
- Never treat a prop as a projection. Treat it as evidence about your projection.

## 5. Red flags and false signals

- A breakout built on fewer than ~250 routes or ~120 carries.
- A "career year" that coincided with a teammate's absence, now healed.
- Preseason box-score production against backups.
- An injury designation that appeared in the last week of camp ("expected back Week 1" is a coin flip).
- A tight end or receiver whose season total is dominated by one game.
- A back whose team added a veteran or spent day-two capital on another back.
- Hype that traces back to one beat writer's tweet rather than usage data.
- A quarterback change that the projection hasn't been updated for.

## 6. Pressure-test template for one player

Use this order for every player the user flags:

1. **The premise.** Restate what the user believes and check it. If a stat is wrong or belongs to another player, say so — that's the highest-value sentence you'll write.
2. **The case for.** Two or three usage numbers with sample sizes, plus the situation (competition, coaching, capital).
3. **The honest risk.** The single most likely way this pick fails, with a number attached.
4. **What Vegas says.** Win total, relevant prop, and what they imply.
5. **Verdict with a price.** "Take at 48, not before." "Smash at 65, pass at 48." "Fade." Always tie the verdict to the user's actual pick numbers and the There % at those picks.

Keep each player under 200 words. The user is comparing seven of them.
