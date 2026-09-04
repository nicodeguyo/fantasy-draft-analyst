# Replacement Level — 2026 draft analysis

**League:** The Sample League · ESPN · 12 teams · snake, pick 5 · half-PPR, 4-pt pass TD, −2 INT · 1 QB / 2 RB / 2 WR / 1 TE / 1 FLEX / K / DEF · one keeper at original round
**Draft:** Sunday, September 6, 2026 · **Written:** Thursday, September 3, 2026 (regenerated Sept 4 on the flex-equilibrium replacement model)
**Projections:** mine (built Sept 3 from 2025 production and 2026 roles, scored in this league's system). **ADP:** ESPN column of the Footballguys cross-platform table for the top 100 (fetched Sept 3), FantasyFootballCalculator half-PPR mocks Aug 28–Sep 2 for the spread and for everyone deeper. **Availability:** 1,500-run Monte Carlo (`draft_sim.py`); the full name × pick matrix is in `sim_availability.csv`.

---

## 1. Verdict: keep Chase Brown

Still the keep, by a clear margin — but a smaller one than a naive model gives him. Brown costs your round-6 pick (overall 68) and is drafted 10th overall on ESPN. Three other players on your roster are worth keeping in principle; none is worth half as much.

### The keeper math

Your picks at slot 5 in a 12-team snake: 5, 20, 29, 44, 53, **68 (forfeited for Brown)**, 77, 92, 101, 116, 125, 140, 149, 164, 173.

Surplus in points = the keeper's points over the last startable player at his position, minus the surplus the best player actually available at that pick would have given you (averaged over 400 keeper-free simulations).

| Player | Cost | You pay (pick) | ESPN ADP | Proj | Surplus (picks) | Surplus (points) | Verdict |
|---|---|---|---|---|---|---|---|
| **Chase Brown** (RB) | R6 | 68 | 10 | 230 | +58 | **+35** | Keep |
| Brock Bowers (TE) | R3 | 29 | 26 | 192 | +3 | +15 | Re-draft him at 20 instead |
| Jayden Daniels (QB) | R7 | 77 | 63 | 347 | +14 | +9 | Re-draft him at 53 |
| Tetairoa McMillan (WR) | R5 | 53 | 42 | 200 | +11 | +8 | Re-draft him at 44 |
| Drake London (WR) | R2 | 20 | 20 | 227 | 0 | −3 | No |
| Courtland Sutton (WR) | R8 | 92 | 78 | 165 | +14 | −16 | No |
| Travis Etienne Jr. (RB) | R4 | 44 | 33 | 190 | +11 | −17 | No |
| Jaylen Warren (RB) | waiver | — | 76 | 176 | — | — | Not keepable |

**35 points across a season is 2.1 a week — the gap between a top-8 back and the Warren/Henderson tier that pick 68 actually buys.** The pick-surplus column lies as usual: Sutton shows +14 picks and is a negative keeper, because the 92nd pick and the 68th pick are different currencies.

### Why Brown, beyond the number

- **What the number is, and why it's 35 and not 54.** Replacement level here is computed by flex equilibrium — every flex slot league-wide goes to the best remaining player regardless of position — which prices the last startable back at 164 (RB28) and the last startable receiver at 156 (WR35). A fixed "55% of flex slots go to backs" split priced RB34 at 137 and made Brown look like +54. The equilibrium number is the honest one: nobody flexes a 137-point back over a 156-point receiver. Brown's edge is +35 under it, and still the largest on your roster by 20 points.
- **Keeper inflation is front-loaded.** Twelve keepers leave the pool but twelve picks are forfeited. Measured in the sim, pick 20 buys roughly the ESPN-ADP-28 player (+7.9), pick 29 the ADP-35 player (+6.1), pick 53 the ADP-56 player (+2.9), and by 77 the inflation is half a pick. Brown at 68 is priced against a true round-6 player, and he is a round-1 player.
- **The player.** 1,019 rushing yards, a Bengals-record 69 catches for 437, 11 TDs in 2025; 18.2 touches and 100 yards a game from Week 6 on (Bengals.com, June 25; FantasyPros, fetched Sept 3). 69% of snaps in the preseason opener to Perine's 31% (Aug 14). Burrow back. No injury news in the last 72 hours; extension talks since January, no holdout.
- **The honest bear case.** The market's median is below mine: Sharp Football (Aug 31) quotes **824.5 rushing yards (−110)** and **5.5 rushing TDs (−125)**, 1,000+ at +210 — roughly 210–220 points in this scoring, not 230. At 215 he is +20 over pick 68, 1.2 a week; still the keep, but the cushion is a real one. Bengals win total 10.5, under favored (−120, BetMGM via VegasInsider, Sept 2).

### The one thing you must confirm first

That your commissioner's keeper sheet lists Brown at **round 6** and that the league is same-round, not round-minus-one. If it is round-minus-one, Brown costs pick 53 instead of 68 — still +30 and still the keep. Also confirm that **waiver pickups are not keepable**: if Warren were keepable at the last round, he'd be a +12 keeper at a round-15 cost — not close to Brown, but worth a second roster spot in some leagues.

### Why not the tempting alternatives

**Brock Bowers (R3, +15).** A positive keeper now — but a round-3 cost for a player ESPN drafts 26th, and the sim says he's still there at your pick 20 **52% of the time** (McBride 72%). Same tight end, a round-2 pick instead of a round-3 pick, and you keep Brown. Both TEs go before 20 in about one draft in nine; then London (60%).

**Jayden Daniels (R7, +9) and Tetairoa McMillan (R5, +8).** Both mildly positive, both re-draftable: Daniels is 50% there at 53 and Hurts 67%; McMillan is 62% there at 44 and Garrett Wilson 83%. Neither is worth forfeiting Brown's +35.

**Drake London (R2, −3).** ESPN ADP 20, your pick 20. Pick 20 in this room returns Bowers/McBride/London himself at +68 to +76; keeping him buys nothing.

### What you sacrifice by keeping nobody

You draft at 68, where the best available surplus averages +31 — a Tuten or a Henderson — and give up 35 points for a 15th roster spot. Dominated.

---

## 2. The number that drives everything

Replacement level in a 12-team, one-flex league, in your scoring, by flex equilibrium (dedicated slots first, then the 12 flex slots and 3 bye/injury slots to the best remaining player regardless of position):

| Pos | Replacement | Who that is |
|---|---|---|
| QB | 312 | QB12 (Kyler Murray) |
| RB | 164 | RB28 (DK Metcalf-level; Tony Pollard) |
| WR | 156 | WR35 (Christian Watson) |
| TE | 116 | TE13 (Mark Andrews) |

The flex slots fill **4 RB / 11 WR / 0 TE**: the receiver pool is deeper, so the marginal back and the marginal receiver land within eight points of each other. That is the number that flips this board from the running-back build a fixed split produces to the one below. Zay Flowers (215) is +59; Breece Hall (203) is +39. Kyren Williams (203) out-projects Tetairoa McMillan (200) and McMillan is the better pick by five. And the 28th back is the *last* one you'll ever have to start — which is why your second running back can wait until pick 77.

---

## 3. Pick geometry and the position plan

Ladder with the keeper round removed: **5 · 20 · 29 · 44 · 53 · 77 · 92 · 101 · 116 · 125 · 140 · 149 · 164 · 173.**

Slot 5 is a middle slot: no paired turn, picks alternate 15 and 9 apart. Every player whose ADP sits between your picks is a now-or-never decision. The 15-pick gaps (5→20, 29→44, 53→77) are where tiers vanish; the 9-pick gaps (20→29, 44→53) are where a player you passed on is still there a third of the time.

The twelve keepers, measured in the sim as net inflation: **+11 at pick 5, +8 at 20, +6 at 29, +4 at 44, +3 at 53, half a pick at 77, nothing from 92 on.** Plan for it in rounds 1–3 and ignore it after round 5.

### The position plan — expected best surplus still available, by position, at each of your picks

| Pick | QB | RB | WR | TE |
|---|---|---|---|---|
| 5 | +43 | +91 | **+106** | +74 |
| 20 | +36 | +45 | +68 | **+69** |
| 29 | +35 | +38 | **+57** | +47 |
| 44 | +34 | +29 | **+42** | +36 |
| 53 | +30 | +17 | +33 | **+34** |
| 77 | +14 | +11 | **+18** | +16 |
| 92 | +11 | −15 | +11 | +6 |
| 101 | +9 | −25 | −1 | +6 |
| 116 | +3 | −36 | −7 | +4 |

**Reading it:** receiver carries the most value at 5 and stays positive through 92, tight end has one window at 20 (tied with WR) and a second at 53, and running back surplus falls from +45 at 20 to +11 at 77 and is negative from 92 on — so your second back must come by 77, not before. Quarterback is flat (+43 to +30) through 53 and halves at 77, so 53 is the quarterback pick.

### What ESPN ADP does that the mock ADP doesn't

`players.csv` came with FantasyFootballCalculator mock ADP. The Footballguys ESPN column shows how an ESPN room differs (picks 5–92; mock There % from a comparison run on `players_mock-adp.csv`, opponent behavior identical):

| Player | Mock ADP | ESPN ADP | Δ | What it means for you |
|---|---|---|---|---|
| Josh Allen | 32 | 18 | −14 | QBs go a round-plus early on ESPN |
| Lamar Jackson | 56 | 40 | −16 | " |
| Jalen Hurts | 82 | 64 | −18 | " |
| Jayden Daniels | 72 | 63 | −9 | 50% at 53 (mock: 80%), gone by 77 |
| Brock Bowers | 41 | 26 | −15 | TE1s go in round 2 on ESPN: 52% at 20 vs 88% in mocks |
| Trey McBride | 38 | 27 | −11 | 72% at 20, **15% at 29** (mock: 80%) |
| Colston Loveland | 59 | 41 | −18 | 16% at 44 (mock: 87%) |
| Sam LaPorta | 116 | 65 | −51 | ESPN's rank pulls him four rounds early |
| Kyle Pitts Sr. | 94 | 74 | −20 | 16% at 77 (mock: 88%) |
| Kraft / Fannin / Kittle | 90 / 81 / 90 | 72 / 66 / 79 | −18 / −15 / −11 | The whole TE middle goes in rounds 6–7 |
| Omarion Hampton | 23 | 17 | −6 | 26% at 20 (mock: 73%) |
| Zay Flowers | 23 | 34 | **+11** | 83% at 29 vs 18% in mocks |
| Rashee Rice | 18 | 23 | +5 | 79% at 20 vs 29% |
| Tetairoa McMillan | 31 | 42 | +12 | 62% at 44 (mock: 0%) |
| Garrett Wilson | 31 | 45 | +14 | 83% at 44 (mock: 1%) |
| Davante Adams / Jameson Williams | 38 / 39 | 53 / 56 | +15 / +17 | 86–89% at 53 (mock: ~0%) |
| Terry McLaurin | 46 | 57 | +11 | 90% at 53 vs 29% |
| Jaylen Warren | 63 | 76 | +13 | 89% at 77 vs 11% |
| Brian Thomas Jr. | 72 | 84 | +12 | 92% at 77, 47% at 92 (mock: 2%) |

ESPN drafters follow ESPN's default ranks, which push QBs and TEs up and let the WR band from ADP 30 to 90 slide 10–17 picks. **In a league where receiver surplus holds value through pick 92, that slide is the whole draft: pay for the tight end at 20 where the room prices him correctly, then let the room hand you receivers a round late at 29, 44 and 92.**

---

## 4. The board — top five at each pick

Ranked by surplus. There % = still on the board at that pick across 1,500 ESPN-priced simulations with twelve keepers drawn.

### Pick 5 (R1) — Wide receiver. Bijan if he fell (21%); otherwise Jaxon Smith-Njigba. Chase or Nacua if JSN is gone; St. Brown last.

| Player | Pos | Proj | Surplus | There % |
|---|---|---|---|---|
| Bijan Robinson | RB | 282 | +118 | 21% |
| Jaxon Smith-Njigba | WR | 268 | +112 | 63% |
| Ja'Marr Chase | WR | 261 | +105 | 31% |
| Puka Nacua | WR | 259 | +103 | 40% |
| Amon-Ra St. Brown | WR | 243 | +87 | 75% |

Gibbs is gone before 5 in 86% of drafts. Under the equilibrium model this is no longer a coin flip with Taylor (+77, 52%) — the WR tier-1 cliff below JSN is 16 points and the RB tier-2 backs are +70 to +77. Chase (leg hyperextension Aug 25, fine) and Nacua (psoas, returned Aug 30) both carry a draft-week flag; JSN doesn't. If all four of Bijan, JSN, Chase and Nacua are gone, St. Brown (75%).

### Pick 20 (R2) — Tight end. Bowers if he's there (52%). Otherwise McBride (72%). Drake London (60%) only if both are gone.

| Player | Pos | Proj | Surplus | There % |
|---|---|---|---|---|
| Brock Bowers | TE | 192 | +76 | 52% |
| Drake London | WR | 227 | +71 | 60% |
| Trey McBride | TE | 184 | +68 | 72% |
| Zay Flowers | WR | 215 | +59 | 87% |
| Rashee Rice | WR | 214 | +58 | 79% |

The 25-point TE cliff below McBride closes here (15% at 29); the receivers don't — Flowers is 83% at 29 and London is the only one of these who won't survive. Bowers is fully healthy with Cousins named the starter and was 12.0 a game in his 12 games last year. Hampton (+47, 26%) and Kyren (+39, 84%) are the backs; neither is close.

### Pick 29 (R3) — Wide receiver. Zay Flowers (83%). Nico Collins if he fell (22%). McMillan is the fallback and survives to 44.

| Player | Pos | Proj | Surplus | There % |
|---|---|---|---|---|
| Trey McBride | TE | 184 | +68 | 15% |
| Zay Flowers | WR | 215 | +59 | 83% |
| Nico Collins | WR | 211 | +55 | 22% |
| Tetairoa McMillan | WR | 200 | +44 | 88% |
| Colston Loveland | TE | 159 | +43 | 80% |

Flowers was WR7 in half-PPR (86 / 1,211 / 5, 55.9% of Ravens WR targets), PFF's 3rd in YPRR (2.53), on the league's highest win total (11.5), and ESPN rooms take him 11 picks later than mocks do. The caveat: he sat out team drills Sept 1–2 (lower body) and is "expected full-go next week" — check Friday; if doubtful, McMillan. Hall (+39, 88%) is the best back here and loses by 20.

### Pick 44 (R4) — Wide receiver. Tetairoa McMillan (62%). Garrett Wilson (83%) if he's gone; Egbuka (80%) only after a full Friday practice.

| Player | Pos | Proj | Surplus | There % |
|---|---|---|---|---|
| Tetairoa McMillan | WR | 200 | +44 | 62% |
| Colston Loveland | TE | 159 | +43 | 16% |
| Tee Higgins | WR | 197 | +41 | 24% |
| Breece Hall | RB | 203 | +39 | 32% |
| Emeka Egbuka | WR | 192 | +36 | 80% |

This is your flex. McMillan (ESPN 42 vs 31 in mocks) is the receiver this room lets fall. Hall is the one back worth a thought — he'd be your RB2 at +39 instead of Warren at +12 — but he's 32% here and taking him means Warren-tier at flex; the receiver path is +12 to +17 better. Irving (+24, 71%) is the RB fallback if the receivers somehow vanish.

### Pick 53 (R5) — Quarterback. Daniels if he's there (50%); Hurts (67%) if not. Otherwise Pitts or Tyler Warren if you have no tight end, or Jameson Williams.

| Player | Pos | Proj | Surplus | There % |
|---|---|---|---|---|
| Emeka Egbuka | WR | 192 | +36 | 21% |
| Garrett Wilson | WR | 191 | +35 | 35% |
| Jayden Daniels | QB | 347 | +35 | 50% |
| Tyler Warren | TE | 151 | +35 | 68% |
| Kyle Pitts Sr. | TE | 150 | +34 | 86% |

The QB column is flat from 5 to 53 and halves at 77; every QB in the 340s is gone by 77 in this ESPN room. Daniels over Hurts (+28). If both are gone, Jameson Williams (89%) or Adams (86%) and get Mahomes at 92 (67%) or Dart at 101 (76%) — about five points across the season.

### Pick 77 (R7) — Running back. Jaylen Warren (89%). Pollard (82%) or Henderson (63%) if he's gone. Parker Washington (46%) only if you already have two backs.

| Player | Pos | Proj | Surplus | There % |
|---|---|---|---|---|
| Kyle Pitts Sr. | TE | 150 | +34 | 16% |
| Parker Washington | WR | 176 | +20 | 46% |
| Harold Fannin Jr. | TE | 133 | +17 | 23% |
| Brian Thomas Jr. | WR | 171 | +15 | 92% |
| Mike Evans | WR | 171 | +15 | 41% |

Warren (176, +12, 89%) is sixth by surplus and the pick anyway: this is the last turn where the RB column is positive, the lineup needs a second back, and every receiver above him is either gone by 92 (Washington, Evans) or still there (Thomas, 47%). He splits with Dowdle under McCarthy (RotoWire, Sept 3) — priced into 176. Henderson sat out Thursday (ankle).

### Pick 92 (R8) — Wide receiver. Brian Thomas Jr. (47%), then Pierce (55%) or Metcalf (80%). Mahomes (67%) if you still have no quarterback.

| Player | Pos | Proj | Surplus | There % |
|---|---|---|---|---|
| Brian Thomas Jr. | WR | 171 | +15 | 47% |
| Patrick Mahomes | QB | 326 | +14 | 67% |
| Alec Pierce | WR | 165 | +9 | 55% |
| DK Metcalf | WR | 164 | +8 | 80% |
| Travis Kelce | TE | 122 | +6 | 96% |

Thomas (ESPN 84 vs mock 72) practiced fully Wednesday after a shoulder issue and is your WR4 and injury insurance. The RB column is −15 here: every back left is below replacement.

### Pick 101 (R9) — Quarterback if you still don't have one (Mahomes 45%, Dart 76%). Otherwise Croskey-Merritt (71%) as RB3, or Kelce (89%) as a TE2.

| Player | Pos | Proj | Surplus | There % |
|---|---|---|---|---|
| Patrick Mahomes | QB | 326 | +14 | 45% |
| DK Metcalf | WR | 164 | +8 | 33% |
| Travis Kelce | TE | 122 | +6 | 89% |
| Jaxson Dart | QB | 318 | +6 | 76% |
| Isaiah Likely | TE | 118 | +2 | 97% |

Picks 116 and 125: nothing above replacement except Kelce (49%) / Likely (81%) as TE2s and Kyler Murray (99%) as a free QB2. Use them on the players in §8.

---

## 5. Tiers with cliffs

Built from projection gaps, not rounds. ★ = yours or targeted. ADP shown is ESPN where available.

**Running back** — replacement 164, 28 get started weekly
- **Tier 1 — win the league alone:** Gibbs (DET, 1, 288), Bijan (ATL, 2, 282)
- **Cliff −41.** Both go top-2 in every ESPN draft. Assume gone.
- **Tier 2 — the only backs worth a first-round pick:** Taylor (IND, 5, 241), Cook (BUF, 9, 237), McCaffrey (SF, 7, 234), Achane (MIA, 11, 234), ★ **Chase Brown** (CIN, 10, 230), Barkley (PHI, 14, 229)
- **Cliff −13.**
- **Tier 3 — starters, but +39 to +47:** Henry (BAL, 13, 216), Hampton (LAC, 17, 211), Walker (KC, 16, 210), Kyren (LAR, 25, 203), Breece Hall (NYJ, 38, 203)
- **Cliff −10.** In this league a tier-3 back is worth less than a tier-4 receiver. Don't pay round 2 for one.
- **Tier 4 — committee backs, +23 to +29:** Javonte (DAL, 30, 193), Jeanty (LV, 22, 191), Etienne (NO, 33, 190), Swift (CHI, 35, 190), Skattebo (NYG, 36, 189), Love (ARI, 32, 188), Irving (TB, 43, 188), Jacobs (GB, 60, 187)
- **Cliff −8.**
- **Tier 5 — your RB2 tier, rounds 5–7:** Judkins (CLE, 47, 179), Montgomery (HOU, 48, 176), Tuten (JAX, 54, 176), ★ Warren (PIT, 76, 176)
- **Cliff −8.** Warren is the tier's cheapest member by 22 picks and 89% there at 77.
- **Tier 6 — replacement:** Henderson (NE, 71, 168), Stevenson (NE, 68, 166), Pollard (TEN, 73, 164)
- **Cliff −11.** Below here every back is bench depth. Price (SEA, 52, 153), Dowdle (PIT, 77, 153), Dobbins (DEN, 86, 148), Harvey (DEN, 94, 142), Croskey-Merritt (WAS, 103, 137), Hubbard (CAR, 107, 137).

**Wide receiver** — replacement 156, 35 get started weekly
- **Tier 1:** ★ Smith-Njigba (SEA, 6, 268), Chase (CIN, 3, 261), Nacua (LAR, 4, 259)
- **Cliff −16.** Chase (leg) and Nacua (psoas) carry a draft-week flag; JSN doesn't.
- **Tier 2:** St. Brown (DET, 8, 243), Lamb (DAL, 12, 237), Jefferson (MIN, 15, 231), London (ATL, 20, 227)
- **Cliff −12.**
- **Tier 3 — the ESPN discount tier:** ★ Flowers (BAL, 34, 215), Rice (KC, 23, 214), A.J. Brown (NE, 19, 211), Pickens (DAL, 21, 211), Collins (HOU, 24, 211)
- **Cliff −11.** Flowers goes 11 picks later on ESPN than in mocks; Rice five.
- **Tier 4 — deep and flat, rounds 3–5:** ★ McMillan (CAR, 42, 200), Nabers (NYG, 29, 197 — ACL, Week 1 unconfirmed), Higgins (CIN, 37, 197), ★ Egbuka (TB, 44, 192 — toe), G. Wilson (NYJ, 45, 191), Olave (NO, 28, 189), McConkey (LAC, 39, 189), D. Smith (PHI, 31, 187), Jameson Williams (DET, 56, 187), Adams (LAR, 53, 186)
- **Cliff −6.**
- **Tier 5 — WR4 and flex, rounds 6–8:** McLaurin (WAS, 57, 180), Odunze (CHI, 61, 180), P. Washington (JAX, 70, 176), ★ Waddle (DEN, 46, 174), Evans (SF, 67, 171), ★ B. Thomas (JAX, 84, 171), DJ Moore (BUF, 50, 169), ★ Burden (CHI, 58, 168), Harrison (ARI, 69, 166), Sutton (DEN, 78, 165), Pierce (IND, 85, 165), Metcalf (PIT, 89, 164)
- **Cliff −8.** Watson (GB, 62, 156) is replacement.

**Tight end** — replacement 116, 13 get started weekly
- **Tier 1:** ★ Bowers (LV, 26, 192), McBride (ARI, 27, 184)
- **Cliff −25.** The largest gap on the board after Tier-1 RB. Pay at 20 or skip to Tier 2 at 53.
- **Tier 2:** ★ Loveland (CHI, 41, 159), T. Warren (IND, 55, 151), ★ Pitts (ATL, 74, 150)
- **Cliff −14.**
- **Tier 3 — usable:** Kraft (GB, 72, 136), Fannin (CLE, 66, 133), Kittle (SF, 79, 129), LaPorta (DET, 65, 125), Kelce (KC, 124, 122)
- **Tier 4 — free:** Goedert, Likely, Andrews (116–118)

**Quarterback** — replacement 312, 12 get started weekly
- **Tier 1:** Allen (BUF, 18, 357)
- **Tier 2:** ★ Daniels (WAS, 63, 347), Lamar (BAL, 40, 344), Hurts (PHI, 64, 340)
- **Cliff −9.**
- **Tier 3:** Maye (NE, 51, 331), Burrow (CIN, 49, 329), Mahomes (KC, 104, 326), Prescott (DAL, 59, 324)
- **Cliff −6.**
- **Tier 4 — replacement:** Dart (NYG, 117, 318), Herbert (LAC, 83, 315), C. Williams (CHI, 75, 314), Murray (MIN, 136, 312)

QB1 to QB8 is 33 points — under two a week — which is why the position waits until the Daniels/Hurts window at 53.

---

## 6. Your guys, pressure-tested

**Bhayshul Tuten (RB, JAX) — proj 176 (cut from 200), +12.**
*Premise:* "gets 60% of the Jaguars' carries." **Wrong.** Liam Coen, Aug 26 (Yahoo): "We're going to have to be a little bit more by committee." Camp settled into a three-back rotation — Tuten on early downs, Chris Rodriguez Jr. (a $10M free agent who played for Coen at Kentucky) between the tackles and at the goal line, LeQuint Allen on third downs (FFC news, Aug 25–Sept 2). Rodriguez had offseason foot surgery, returned to camp July 30 and plans to play Week 1. *The case for:* Coen publicly wants him to "go be special"; camp reports say he took the majority of first-team reps; the team calls him a potential "complete No. 1" (Sept 2). 4.28 speed, and 5 rushing TDs on only 83 carries as a rookie (307 yards, 3.7 YPC). *The risk:* he was sent home sick Sept 2 (expected Week 1), and a 3.7-YPC back sharing goal-line work with a Coen favorite is a 150-point outcome. *Vegas:* Jaguars 8.5, over −140. *Price:* 79% at 53, 0% at 77. **Verdict: PASS.** At 53 he's +12 in a slot where Daniels is +35; and Warren, the same 176, is 89% there at 77.

**Luther Burden III (WR, CHI) — proj 168, +12.**
*Premise:* "3rd in YPRR last year behind Puka and JSN." **True on CBS's measure (2.71, 3rd of 152), not on PFF's (2.34, tied 7th)** — and either way it came on **307 routes**, the fewest of anyone in the top 10 (PFF, July 7). *The case for:* 7.4% target share weeks 1–10, 18.4% weeks 11–17, a 26.8% target rate per route (Bleacher Nation, Aug 10); DJ Moore is in Buffalo; Ben Johnson says he's "buying Burden stock." *The risk:* Odunze is healthy and Loveland led the team in targets per route (29.1%); Burden's surge pace is 105 targets — a WR3, which is exactly his 168. *Vegas:* Bears 9.5, under −125. *ESPN price:* 58 (mock 56) — no discount. *Price:* 89% at 53, 1% at 77. **Verdict: PASS.** He's +12; Jameson Williams and Adams are +30 at the same pick and 86–89% there.

**Emeka Egbuka (WR, TB) — proj 192 (cut from 206), +36.**
*Premise:* "Evans left Tampa." **True** — three-year deal with the 49ers, reported March 9. *The case for:* 127 targets as a rookie (63 / 938 / 6 in 17 games), 29.4% first-read target share, 2.49 YPRR in the five weeks before Mayfield's injury; Godwin is 30 and had 360 yards; the Bucs are moving him to the Z. *The risk is the one you can see:* sprained toe Aug 12, no preseason snaps, still not in team drills as of Sept 2 — Bowles: "Headed in the right direction. I don't know how fast." I priced roughly a game and a half of missed or limited time. *Vegas:* Bucs 8.5, under −135. *Price:* 80% at 44, 21% at 53. **Verdict: OK at 44 — as the Plan B behind McMillan (+44) and Garrett Wilson (+35, 83%), and only if he practices fully Friday.**

**Jaylen Waddle (WR, DEN) — proj 174, +18.**
*Premise:* "Denver threw the most in the league." **True:** Bo Nix threw 612 passes, most in the NFL, at 6.4 yards per attempt, 28th of 33 (DenverSports, Aug 11). *The case for:* Denver paid a 1st, 3rd and 4th for him; Payton says he'll "play everywhere except offensive line"; 64 / 910 / 6 with bad QB play, WR24. Receiving-yards prop 899.5 (Yahoo, Aug 24) — consistent with my 174. *The risk:* Sutton is still the red-zone target and a 14-3 team that just added a receiver throws 560 times, not 612. *Price:* 77% at 44, 30% at 53. **Verdict: PASS at 44; OK at 53 only if Daniels, Hurts and the tier-4 receivers are all gone.**

**Kyle Pitts Sr. (TE, ATL) — proj 150, +34.**
*Premise:* "finished TE2." **True and hollow.** TE2 by total (166.8, 88 / 928 / 5), TE6 per game (9.8), 86 points behind McBride, three of his five TDs in one game. *The case for:* Stefanski's Cleveland tight ends were 2nd in the NFL in targets 2020–25; a 3-yr/$54M extension; consensus ~111 targets (Footballguys, July 29). *The risk:* Atlanta still hasn't named a QB — Penix (ACL) vs Tua; NFL Network says Penix "eventually" (Sept 2). Win total 6.5. *ESPN price:* 74 vs 94 in mocks, so **16% at 77** where the mock says 88%. *Price:* 86% at 53. **Verdict: OK at 53 only if you missed both Bowers and McBride at 20** — then he or Tyler Warren (68%) is your tight end, and the QB waits for Mahomes at 92.

**Colston Loveland (TE, CHI) — proj 159, +43.**
*Premise:* "Ben Johnson loves tight ends." **Half right.** LaPorta's 86-catch rookie year came under Johnson, but the better evidence is 2025 itself: Loveland 82 targets / 58 / 713 / 6 in 16 games (TE12) with the team-high 29.1% target rate per route, while Kmet fell to 48 targets. ESPN projects 118 targets. The depth chart listing him "co-starter" with Kmet (RotoWire, Sept 3) is a formality. *The risk:* Odunze, Burden and Swift all need the ball; 159 is a TE3 projection with no cushion. *ESPN price:* 41 vs 59 in mocks — **80% at 29, 16% at 44.** **Verdict: PASS.** At 29 he's +43 against Flowers' +59, and if both TE1s went at 20 the right answer is still Flowers at 29 and Pitts or Tyler Warren at 53 (+34/+35, 86%/68%) — nine points cheaper than Loveland and a round later.

**Three names to add.** **Brian Thomas Jr.** (WR, JAX, ESPN 84 vs mock 72): 171, 92% at 77 and 47% at 92 — your WR4. **Jaylen Warren** (RB, PIT, ESPN 76): 176, 89% at 77 — the RB2 this build waits for. **Garrett Wilson** (WR, NYJ, ESPN 45 vs 31): 191, 83% at 44 — the McMillan fallback that lets you skip Egbuka's toe.

**Reach rule applied to your picks.** The only endorsed reach is a tight end at 20 (role certainty in a tier that ends before 29). Nobody at 44, 53 or 77 earns one: McMillan is 62% at 44 with Wilson 83% behind him, Daniels 50% at 53 with Hurts 67%, Warren 89% at 77. Don't take a running back before 77 for "scarcity" — in this league there isn't any.

---

## 7. Sample drafts and the target build

Across 1,500 ESPN-priced simulations the projected starter total runs **1,785 to 1,912, mean 1,864** (sd 18); the ten sample drafts land between 1,816 and 1,892 — under four and a half a week between the best and the worst, which is the message: structure (Brown kept, WR at 5, TE at 20, receivers at 29 and 44, QB at 53, RB2 at 77) matters more than any single name.

**Most-owned across 1,500 runs (picks 1–8):** Zay Flowers 82%, Jaylen Warren 71%, Jayden Daniels 63%, Brock Bowers 52%, McMillan 51%, Brian Thomas 45%, Smith-Njigba 42%, McBride 31%, Breece Hall 26%, Pierce 24%.

**What happened in essentially every draft:** a Tier-1 tight end at 20 (7 of 10); Flowers at 29 (8 of 10); McMillan at 44 (5 of 10); a quarterback at 44 or 53 (8 of 10) or Mahomes at 77 (2); Warren at 77 (6 of 10); a receiver at 92 in all 10; a running back before 77 in one draft out of ten. The sim's own weakness: it filled RB2 with Henderson (168) twice and left it to Croskey-Merritt (137) in one draft — which is why Warren at 77 is written in ink below, with Pollard (82%) behind him.

**The target build** (There % from `sim.json`):

| Pick | Player | Pos | Proj | There % | If he's gone |
|---|---|---|---|---|---|
| KEEP | Chase Brown | RB | 230 | — | — |
| 5 | Jaxon Smith-Njigba | WR | 268 | 63% | Bijan if he fell (21%); Ja'Marr Chase (31%) / Puka Nacua (40%); Amon-Ra St. Brown (75%) |
| 20 | Brock Bowers | TE | 192 | 52% | Trey McBride (72%); Drake London (60%) if both TEs are gone |
| 29 | Zay Flowers | WR | 215 | 83% | Nico Collins (22%); Tetairoa McMillan (88%) |
| 44 | Tetairoa McMillan | WR | 200 | 62% | Garrett Wilson (83%); Emeka Egbuka (80%) only with a full Friday practice |
| 53 | Jayden Daniels | QB | 347 | 50% | Jalen Hurts (67%); Kyle Pitts (86%) if you still have no TE; Jameson Williams (89%) |
| 77 | Jaylen Warren | RB | 176 | 89% | Tony Pollard (82%); TreVeyon Henderson (63%) |
| 92 | Brian Thomas Jr. | WR | 171 | 47% | Alec Pierce (55%); DK Metcalf (80%); Patrick Mahomes (67%) if no QB |
| 101 | J. Croskey-Merritt | RB | 137 | 71% | Chuba Hubbard (93%); Mahomes (45%) / Jaxson Dart (76%) if no QB |
| 116 | Isaiah Likely | TE | 118 | 81% | Travis Kelce (49%); Kyle Monangai (34%) |
| 125 | Woody Marks | RB | 112 | 94% | KC Concepcion (57%) |
| 140 | Mike Washington Jr. | RB | 95 | 75% | Braelon Allen (13%); Tank Bigsby (98%) |
| 149 | Jordyn Tyson | WR | 100 | 100% | Travis Hunter (100%) |
| 164 | Chase McLaughlin | K | 136 | 50% | Cam Little (34%) |
| 173 | Baltimore Defense | DEF | 103 | 83% | Buffalo Defense (98%) |

Starters: Daniels 347 · Brown 230 · Warren 176 · JSN 268 · Flowers 215 · Bowers 192 · McMillan 200 (flex) · McLaughlin 136 · Baltimore 103 = **1,867**, right at the sim mean with every starter at least a coin flip and two receivers plus a receiver at flex — the lineup the equilibrium model says this league rewards.

**Why this one.** It spends the two steep-surplus picks (5 and 20) on the two positions with the biggest cliffs, buys the two receivers the room under-prices at 29 and 44, takes the quarterback at the last pick where the QB column is still +30, and waits for the second back until the last pick where the RB column is still positive — where your own Warren is 89% there.

**The honest weakness:** RB2. Warren is a timeshare and the backs behind him at 101–125 are below replacement; one Brown injury and you're starting Croskey-Merritt. **The hedge:** Breece Hall at 44 (32%) when McMillan is gone — the flex becomes Thomas at 92 and RB2 becomes a 203, at a cost of about 12 points in the median outcome but with a much better floor.

**The upside case, not the plan:** Bijan at 5 (21%) + Bowers + Flowers + McMillan projects about 1,900. Don't build for it.

### How to use the board on draft day

The board (`draft-board.html`) is this section made tappable, and it works in four steps. **Before the draft**, read *The plan* once — it's the table above with the Plan B beside every pick — and the position roadmap under it, which is the heatmap from §3. **On the clock**, tap your pick number in the top bar and take the highest *Surplus* still on the board, not the biggest name; if your target's *There %* at your next pick is under 50, take him now. **When someone else drafts a player**, tap his name anywhere and he greys out on every list, so the tables stay honest as the room drafts. **When you draft a player**, tap the ✓ on his row: your lineup fills in below the roadmap and shows which starting slots are still open. State is saved in the browser, so a reload mid-draft loses nothing.

---

## 8. The late-round plan (picks 101–173)

- **Handcuffs.** Samaje Perine, Brown's backup, isn't in the pool and won't be drafted — claim him Week 1; he is the one handcuff that matters. Rico Dowdle is gone by 92 (16%), so the Warren side can't be insured; Pollard at 77 as the Plan B is the insurance.
- **Backs below replacement are still your bench.** The RB column is negative from 92 on, which means every back you draft there is a bench player — pick the ones with a path to volume: Croskey-Merritt (71% at 101), Hubbard (93% at 101, 50% at 116), Monangai (85% at 101), Woody Marks (94% at 125).
- **Next-year keeper logic.** Waiver pickups can't be kept, so a round-11+ hit is the only cheap keeper you can manufacture. Bias 125–149 toward Jordyn Tyson (100% at 149), Travis Hunter (100% at 173 — the draft ends before ADP reaches him), Mike Washington (75% at 140, Jeanty's fill-in), Tank Bigsby (98% at 140), Concepcion (57% at 125). A Tyson or Hunter breakout is a round-13 keeper in 2027.
- **QB2 and TE2:** Kyler Murray is 99% there at 116 and Likely 81% — take Likely at 116 (Bowers' knee history), skip the QB2.
- **K and DEF at 164 and 173.** The room starts on kickers and defenses in round 11; Seattle, Denver and Houston are gone by 140, and Baltimore (83%) or Buffalo (98%) is there at 173. McLaughlin (50%) or Little (34%) at 164. Aubrey is 27% at 149 — not worth it.

---

## 9. Assumptions worth checking before you commit

- **Keeper rule:** same-round, Brown at round 6, waiver pickups not keepable. If any of those is wrong, re-read §1.
- **Lineup:** 12 teams, one flex, no superflex. A superflex slot would make Daniels the keeper conversation.
- **15 rounds including K/DEF:** anyone with an ADP past ~155 goes undrafted, which is why the round-13/14 lottery tickets are free.
- **ESPN pricing covers the top 100 only** (Footballguys ESPN column); players 101+ carry mock ADP, so There % past pick 100 is approximate.
- **The one assumption that flips the board:** how your league fills its flex. The equilibrium model assumes managers flex the better player (4 backs / 11 receivers league-wide), which prices RB replacement at 164 and makes receivers the value at 5, 29 and 44. If your leaguemates reflexively flex backs — a fixed 55% split — RB replacement drops to 137, Breece Hall at 44 becomes the pick over McMillan, and Warren is worth taking at 53. Look at last year's Week 10 lineups: if fewer than 30 running backs were started, this board is right; if 34 or more, take the back at 44.
- **Injury flags to re-check Saturday:** Flowers (lower body), Egbuka (toe), Nabers (ACL), Jeanty (ankle), Tuten (sent home sick Sept 2), Nacua (psoas), Chase (leg), Hall (groin), Henderson (ankle). A "did not practice Friday" changes the pick.
- Real leaguemates are less rational than simulated ones. The two who "always take a QB by round 4" push the QB run earlier than ESPN ADP says: Daniels at 53 is less likely than 50%, and the receivers at 53 more likely than 89%.

---

## Appendix

**Terms.** *Replacement level* — points of the worst player at a position who still has to start for someone every week, computed by flex equilibrium (dedicated slots first, then every flex slot league-wide to the best remaining player regardless of position, plus three bye/injury slots). *Flex fill* — how those flex slots split by position once everyone starts their best player; 4 RB / 11 WR / 0 TE here. *Surplus* — projection minus replacement; the number every table is sorted by. *Position plan* — the expected best surplus still available at each position at each of your picks; the answer to "when do I take which position." *There %* — how often the player was still undrafted at that pick across the simulated drafts. *Tier / cliff* — players close enough in projection that the choice barely matters / the point drop between tiers. *Keeper inflation* — with keepers removed, the player available at pick p is worse than ADP p suggests. *Route share, target share, TPRR, YPRR* — share of team pass plays run as routes; share of targets; targets per route; yards per route (unstable under ~250 routes).

**Scoring applied.** 0.1/rush yd, 0.1/rec yd, 0.5/rec, 6/rush or rec TD, 0.04/pass yd, 4/pass TD, −2/INT, −2/fumble lost, 2/two-point; no TE premium, no bonuses.

**Sources and dates.**
- ADP: Footballguys cross-platform table (`footballguys.com/adp?season=2026&pos=all`), ESPN column, fetched Sept 3, 2026 (page prints no date); FantasyFootballCalculator half-PPR 12-team mocks, Aug 28–Sep 2, 2026 (spread and players beyond the top 100); RotoWire ADP page dated Sept 2, 2026 for injury flags. The ESPN API endpoint loaded but returns alphabetical order without the filter header, so the Footballguys column was used as the ESPN price.
- Win totals: VegasInsider (BetMGM lines), Sept 2, 2026.
- Player props: Sharp Football Analysis RB props (Aug 31, 2026) — Brown 824.5 rush yds / 5.5 rush TD, Montgomery 825.5 / 7.5; Yahoo "9 over/under bets" (Aug 24, 2026) — Waddle 899.5 rec yds, Walker 950.5 rush yds, McBride 100.5 rec, Kyren 9.5 rush TD, Achane u1,000, C. Williams 3,645 pass yds, Allen 24.5 pass TD, Lamb 94.5 rec.
- Usage and news (all fetched Sept 3): PFF YPRR leaders (Jul 7); Bleacher Nation on Burden (Aug 10) and Bears TEs (Jul 24); Fantasy Footballers on Egbuka (Jul 10); Yahoo/Coen on the Jaguars committee (Aug 26); SI/Coen (Jul 22); PFT on Rodriguez (Jun 9), Roundtable (Jul 30); FFC player-news pages for Tuten, Waddle, Egbuka, Gibbs, Hampton, Brown, Flowers, Hall, Bowers, Irving (items dated Aug 5–Sept 2); FantasyPros 2025 TE stats and Pitts page; Footballguys Pitts spotlight (Jul 29); Yahoo/Schefter on the Falcons QB (Sept 1); NBC/Wolfe (Sept 2); Athlon on Nabers (Sept 1) and Irving/Gainwell (Jul 7); Pewter Report/Zac Robinson (Aug 5); PFT and Yardbarker on Jeanty (Sept 1); DenverSports on Nix's 612 attempts (Aug 11); RotoWire news feed (Sept 3). ESPN.com articles and Pro Football Rumors did not load (JS/robots).

**Projections I changed (five), from my Sept 3 set:**
1. Emeka Egbuka 206 → 192 — toe sprain, no team drills as of Sept 2; ~1.5 games of lost/limited time.
2. Bhayshul Tuten 200 → 176 — Coen's "by committee" (Aug 26); Rodriguez has the goal line.
3. Bucky Irving 201 → 188 — Gainwell on flat routes and the pony package (OC, Aug 5); Tucker trusted at the goal line (Aug 30); 3.4 YPC in 2025.
4. Malik Nabers 207 → 197 — ACL/meniscus (Wk 4, 2025); won't commit to Week 1 (Sept 1).
5. Ashton Jeanty 199 → 191 — ankle sprain Aug 23, side work only Sept 1; ~1 missed game.

**Simulation settings.** 1,500 runs, seed 1000; keepers drawn (weighted toward better players, rounds correlated to quality — the league hasn't published its list); replacement level by flex equilibrium (QB12 / RB28 / WR35 / TE13 / K12 / DEF12; flex fill 4 RB / 11 WR / 0 TE); opponents draft ADP + noise scaled to each player's spread and capped, with a positional-need bias from round 8 and kickers/defenses on a rising curve from round 11; "me" weighs the opportunity cost of waiting at each position and keeps the bench balanced; my keeper Chase Brown, round 6. Net keeper inflation measured in-sim: +11.2 picks at 5, +7.9 at 20, +6.1 at 29, +3.9 at 44, +2.9 at 53, +0.5 at 77, +0.1 at 92. A 400-run keeper-free pass priced the keeper table; the position plan is the expected best surplus by position at each pick over the same runs. The mock-ADP comparison figures in §3 come from a comparison run on `players_mock-adp.csv` (the pool as delivered, before repricing).

**Assumptions.** Lineup as configured; injuries baked into expected games rather than modeled separately; K/DEF treated as near-interchangeable and drafted last; players not in `players.csv` (e.g., Samaje Perine, Sean Tucker) are waiver-wire, not draft, targets.
