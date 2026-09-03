# Replacement Level — 2026 draft analysis

**League:** The Sample League · ESPN · 12 teams · snake, pick 5 · half-PPR, 4-pt pass TD, −2 INT · 1 QB / 2 RB / 2 WR / 1 TE / 1 FLEX / K / DEF · one keeper at original round
**Draft:** Sunday, September 6, 2026 · **Written:** Thursday, September 3, 2026
**Projections:** mine (built Sept 3 from 2025 production and 2026 roles, scored in this league's system). **ADP:** ESPN column of the Footballguys cross-platform table for the top 100 (fetched Sept 3), FantasyFootballCalculator half-PPR mocks Aug 28–Sep 2 for the spread and for everyone deeper. **Availability:** 1,500-run Monte Carlo (`draft_sim.py`); the full name × pick matrix is in `sim_availability.csv`.

---

## 1. Verdict: keep Chase Brown

It isn't close. Brown costs your round-6 pick (overall 68) and is being drafted 10th overall on ESPN. Nobody else on your roster is worth more than a rounding error at their cost.

### The keeper math

Your picks at slot 5 in a 12-team snake: 5, 20, 29, 44, 53, **68 (forfeited for Brown)**, 77, 92, 101, 116, 125, 140, 149, 164, 173.

Surplus in points = Brown's points over the last startable RB (137) minus the surplus the best player actually available at pick 68 would have given you, averaged over 400 keeper-free simulations.

| Player | Cost | You pay (pick) | ESPN ADP | Surplus (picks) | Surplus (points) | Verdict |
|---|---|---|---|---|---|---|
| **Chase Brown** (RB) | R6 | 68 | 10 | +58 | **+54** | Keep |
| Brock Bowers (TE) | R3 | 29 | 26 | +3 | +11 | Re-draft him at 20 instead |
| Jayden Daniels (QB) | R7 | 77 | 63 | +14 | 0 | No |
| Travis Etienne Jr. (RB) | R4 | 44 | 33 | +11 | −2 | No |
| Tetairoa McMillan (WR) | R5 | 53 | 42 | +11 | −10 | No |
| Drake London (WR) | R2 | 20 | 20 | 0 | −17 | No |
| Courtland Sutton (WR) | R8 | 92 | 78 | +14 | −26 | No |
| Jaylen Warren (RB) | waiver | — | 76 | — | — | Not keepable |

**54 points across a season is 3.2 a week — the gap between a top-8 RB and the Tuten/Montgomery/Warren tier that pick 68 actually buys.** Notice the pick-surplus column lies: Sutton (pick 92) and Daniels (pick 77) both show +14 picks, and neither is worth keeping, because the 68th, 77th and 92nd picks are different currencies. Points-per-pick is steepest at the top.

### Why Brown, beyond the number

- **Keeper inflation is front-loaded here.** Twelve keepers leave the pool, but twelve picks are also forfeited. Measured in the sim, pick 20 buys roughly the ESPN-ADP-28 player (+7.9), pick 29 the ADP-35 player (+6.1), pick 53 the ADP-56 player (+2.9), and by 77 the inflation is half a pick. So Brown at 68 is priced against a true round-6 player, and he is a round-1 player.
- **The player.** 1,019 rushing yards, a Bengals-record 69 catches for 437, 11 TDs in 2025; 18.2 touches and 100 yards a game from Week 6 on (Bengals.com, June 25; FantasyPros, fetched Sept 3). 69% of snaps in the preseason opener to Perine's 31% (Aug 14). Burrow back. No injury news in the last 72 hours; extension talks since January, no holdout.
- **The honest bear case.** The market's median is below mine: Sharp Football (Aug 31) quotes **824.5 rushing yards (−110)** and **5.5 rushing TDs (−125)**, 1,000+ at +210 — roughly 210–220 points in this scoring, not 230. At 215 he is still +39 over pick 68, 2.3 a week; the verdict survives the haircut. Bengals win total 10.5, under favored (−120, BetMGM via VegasInsider, Sept 2).

### The one thing you must confirm first

That your commissioner's keeper sheet lists Brown at **round 6** and that the league really is same-round (not round-minus-one). If it is round-minus-one, Brown costs pick 53 instead of 68 — still +48 and still the keep, but your pick-5 plan below shifts one round. Also confirm that **waiver pickups are not keepable**: if Warren were keepable at the last round, he would be the second-best keeper on the roster (+39 over replacement at a round-15 cost), though still far behind Brown.

### Why not the tempting alternatives

**Brock Bowers (R3, +11).** The only other positive number, and small because ESPN drafts him 26th — right at his cost. Keep Brown, and Bowers goes back in the pool where he is still there at your pick 20 **52% of the time** (McBride 72%). Same tight end, a round-2 pick instead of a round-3 pick, and you keep Brown. Both TEs go before 20 in 11% of drafts; then Loveland at 29 (80%).

**Jayden Daniels (R7, −1).** QB2 (347) at a round-7 cost looks like a gift; it isn't. QB replacement is 312 (Kyler Murray, free in round 12), Daniels is +35 over that, and pick 77 returns +35 on its own. Draft him at 53 if you want him (47% there).

**Drake London (R2, −17).** ESPN ADP 20, your pick 20. Pick 20 in this room returns Bowers/McBride/Kyren at +66 to +78; London is +62 (WR replacement 165). The emotional keep and the wrong one.

### What you sacrifice by keeping nobody

You draft at 68, where the best available surplus averages +39 — a Tuten or a Montgomery — and give up 54 points for a 15th roster spot. Dominated.

---

## 2. The number that drives everything

Replacement level in a 12-team, 1-flex league, in your scoring (padded by three at RB/WR for byes and injuries, one at TE):

| Pos | Replacement | Who that is |
|---|---|---|
| QB | 312 | QB12 (Kyler Murray) |
| RB | 137 | RB34 (Chuba Hubbard / Croskey-Merritt) |
| WR | 165 | WR32 (Sutton / Pierce) |
| TE | 114 | TE14 (Jake Ferguson) |

That **28-point gap** between RB and WR replacement is the entire draft. Zay Flowers projects 215 — twelve more points than Breece Hall's 203 — and Hall is the better pick by surplus (+66 vs +50), because the 32nd receiver you can get for free scores 165 and the 34th back scores 137. It is also why Daniels' 347 (+35) is worth less than Tuten's 176 (+39).

---

## 3. Pick geometry

Ladder with the keeper round removed: **5 · 20 · 29 · 44 · 53 · 77 · 92 · 101 · 116 · 125 · 140 · 149 · 164 · 173.**

Slot 5 is a middle slot: no paired turn, picks alternate 15 and 9 apart. You can't plan two-player combinations; every player whose ADP sits between your picks is a now-or-never decision. The 15-pick gaps (5→20, 29→44, 53→77) are where tiers vanish; the 9-pick gaps (20→29, 44→53) are where a player you passed on is still there a third of the time.

The twelve keepers, measured in the sim as net inflation (how many more players are gone than the pick number implies): **+11 at pick 5, +8 at 20, +6 at 29, +4 at 44, +3 at 53, half a pick at 77, nothing from 92 on.** Pick 20 buys roughly the ESPN-ADP-28 player; pick 77 buys the ADP-77 player, because by then the twelve forfeited picks have caught up with the twelve removed keepers. Plan for inflation in rounds 1–3 and ignore it after round 5.

### What ESPN ADP does that the mock ADP doesn't

`players.csv` came with FantasyFootballCalculator mock ADP. The Footballguys ESPN column shows how an ESPN room differs (picks 5–92):

| Player | Mock ADP | ESPN ADP | Δ | What it means for you |
|---|---|---|---|---|
| Josh Allen | 32 | 18 | −14 | QBs go a round-plus early on ESPN |
| Lamar Jackson | 56 | 40 | −16 | " |
| Jalen Hurts | 82 | 64 | −18 | " |
| Jayden Daniels | 72 | 63 | −9 | 47% at 53 (mock: 80%), gone by 77 |
| Brock Bowers | 41 | 26 | −15 | TE1s go in round 2 on ESPN: 52% at 20 vs 88% in mocks |
| Trey McBride | 38 | 27 | −11 | 72% at 20, **15% at 29** (mock: 80%) |
| Colston Loveland | 59 | 41 | −18 | 17% at 44 (mock: 87%) |
| Sam LaPorta | 116 | 65 | −51 | ESPN's rank pulls him four rounds early |
| Kyle Pitts Sr. | 94 | 74 | −20 | 16% at 77 (mock: 88%) |
| Kraft / Fannin / Kittle | 90 / 81 / 90 | 72 / 66 / 79 | −18 / −15 / −11 | The whole TE middle goes in rounds 6–7 |
| Omarion Hampton | 23 | 17 | −6 | 26% at 20 (mock: 73%) |
| Zay Flowers | 23 | 34 | **+11** | 85% at 29 vs 18% in mocks |
| Rashee Rice | 18 | 23 | +5 | 79% at 20 vs 29% |
| Tetairoa McMillan | 31 | 42 | +12 | 66% at 44 (mock: 0%) |
| Garrett Wilson | 31 | 45 | +14 | 83% at 44 (mock: 1%) |
| Davante Adams / Jameson Williams | 38 / 39 | 53 / 56 | +15 / +17 | 86–89% at 53 (mock: ~0%) |
| Terry McLaurin | 46 | 57 | +11 | 90% at 53 vs 29% |
| Jaylen Warren | 63 | 76 | +13 | 90% at 77 vs 11% |
| Brian Thomas Jr. | 72 | 84 | +12 | 93% at 77, 49% at 92 (mock: 2%) |

ESPN drafters follow ESPN's default ranks, which push QBs and TEs up and let the WR band from ADP 30 to 90 slide 10–17 picks. **The exploit: pay for the tight end at 20 where the room prices him correctly, then let the room hand you receivers a round late at 29, 44 and 53.** Every There % below is from the ESPN-priced simulation; the mock figures come from the same simulator run on `players_mock-adp.csv` (the pool as delivered, before repricing).

---

## 4. The board — top five at each pick

Ranked by surplus. There % = still on the board at that pick across 1,500 ESPN-priced simulations with twelve keepers drawn.

### Pick 5 (R1) — Running back if Bijan fell (21%). Otherwise Smith-Njigba, with Taylor as the tiebreak loser.

| Player | Pos | Proj | Surplus | There % |
|---|---|---|---|---|
| Bijan Robinson | RB | 282 | +145 | 21% |
| Jonathan Taylor | RB | 241 | +104 | 52% |
| Jaxon Smith-Njigba | WR | 268 | +103 | 63% |
| James Cook III | RB | 237 | +100 | 76% |
| Christian McCaffrey | RB | 234 | +97 | 68% |

Gibbs is gone before 5 in over 85% of drafts. Taylor and Smith-Njigba are a one-point coin flip on surplus; JSN wins because the WR tier-1 cliff below him is 16 points, Taylor was RB22 per game without Daniel Jones last year (Jones is back off an Achilles, unproven), and the backs you want at 20 and 29 survive at 85%+. Achane (+97, 81%) is sixth and loses on touch volume — his rushing-yards under 1,000 is a featured play in the Aug 24 props piece. If Bijan, JSN and Taylor are all gone (14%), Cook.

### Pick 20 (R2) — Tight end. Bowers if he's there. Otherwise McBride. Kyren Williams only if both are gone.

| Player | Pos | Proj | Surplus | There % |
|---|---|---|---|---|
| Brock Bowers | TE | 192 | +78 | 52% |
| Omarion Hampton | RB | 211 | +74 | 26% |
| Kenneth Walker | RB | 210 | +73 | 21% |
| Trey McBride | TE | 184 | +70 | 72% |
| Kyren Williams | RB | 203 | +66 | 84% |

The 25-point cliff below McBride is the biggest on the board after the top two backs, and it closes here: McBride is 15% there at 29. Kyren (84%) and Hall (88%) are both waiting at 29, so the tight end costs you nothing at RB. Both TE1s are gone in 11% of drafts; then Kyren, or London (+62, 60%). Bowers is fully healthy with Cousins named the starter and was 12.0 a game in his 12 games last year — take him over McBride when both are there.

### Pick 29 (R3) — Zay Flowers. Kyren Williams if he fell. Breece Hall is the safe third choice.

| Player | Pos | Proj | Surplus | There % |
|---|---|---|---|---|
| Breece Hall | RB | 203 | +66 | 88% |
| Kyren Williams | RB | 203 | +66 | 31% |
| Javonte Williams | RB | 193 | +56 | 72% |
| Travis Etienne Jr. | RB | 190 | +53 | 84% |
| D'Andre Swift | RB | 190 | +53 | 84% |

McBride (+70) is 15% here. Flowers (215, +50, 85%) is outside the top five by surplus and the pick anyway, because of what's left at 44: Flowers is gone by then (2%), while Irving (+51) is there 71%, Jacobs (+50) 60% and Judkins (+42) 83%. Flowers-then-Irving gives 215 + 188 at WR2/RB2; Hall-then-Jameson-Williams gives 203 + 187 — twelve points, plus you land the tier-3 receiver ESPN rooms uniquely let fall (mocks take him at 23). Flowers was WR7 in half-PPR (86/1,211/5, 55.9% of Ravens WR targets), PFF's 3rd in YPRR (2.53), on the league's highest win total (11.5). The caveat: he sat out team drills Sept 1–2 (lower body) and is "expected full-go next week" — check Friday; if doubtful, Hall. If Kyren is there (31%), take him over Flowers; a tier-3 back is scarcer and McMillan (66%) covers WR2 at 44.

### Pick 44 (R4) — Running back. Bucky Irving. Josh Jacobs if Irving is gone. Breece Hall if he somehow fell.

| Player | Pos | Proj | Surplus | There % |
|---|---|---|---|---|
| Breece Hall | RB | 203 | +66 | 23% |
| Bucky Irving | RB | 188 | +51 | 71% |
| Josh Jacobs | RB | 187 | +50 | 60% |
| Colston Loveland | TE | 159 | +45 | 17% |
| Quinshon Judkins | RB | 179 | +42 | 83% |

Irving's projection is already cut to 188 for the Gainwell/Tucker committee (§6). Jacobs (187, 60%) is the same tier and the first fallback — he showed 22% here before the simulator stopped over-drafting wide-spread ADPs — and he's 31% at 53, so Irving first. Judkins (83%) and Montgomery (86%) survive to 53 about half the time (42%, 54%), which is why you don't take them here. McMillan (200, +35, 66%) is the receiver if you took a back at 29.

### Pick 53 (R5) — Quarterback. Daniels if he's there. Otherwise a receiver: Jameson Williams, Adams or McLaurin, whichever ran the most routes last week.

| Player | Pos | Proj | Surplus | There % |
|---|---|---|---|---|
| Josh Jacobs | RB | 187 | +50 | 31% |
| Quinshon Judkins | RB | 179 | +42 | 42% |
| Jaylen Warren | RB | 176 | +39 | 93% |
| David Montgomery | RB | 176 | +39 | 54% |
| Bhayshul Tuten | RB | 176 | +39 | 78% |

Daniels (347, +35, 47%) sits eighth by surplus. This is where the "QB in round 7 or later" rule breaks: in an ESPN room every QB in the 340s is gone by 77, the receivers here are +15 to +22, and Warren survives to 77 (90%), so you don't need the back. Daniels over Hurts (68%, +28). If both are gone, take the WR and get Mahomes (81% at 92) or Dart (75% at 101) — about five points across the season.

### Pick 77 (R7) — Running back. Jaylen Warren. Parker Washington if you skipped WR at 53.

| Player | Pos | Proj | Surplus | There % |
|---|---|---|---|---|
| Jaylen Warren | RB | 176 | +39 | 90% |
| Kyle Pitts Sr. | TE | 150 | +36 | 16% |
| TreVeyon Henderson | RB | 168 | +31 | 63% |
| Rhamondre Stevenson | RB | 166 | +29 | 50% |
| Tony Pollard | RB | 164 | +27 | 82% |

Warren is the best surplus at 77 and the sim's most-owned player (88% of runs); the Dowdle split (RotoWire, Sept 3) is priced into 176. Henderson sat out Thursday (ankle); skip. Washington (176, +11, 45%) is the WR2 if you went Daniels at 53.

### Pick 92 (R8) — Mahomes if you still have no quarterback (81% here, 39% at 101). Otherwise wide receiver: Brian Thomas Jr., then Pierce or Metcalf.

| Player | Pos | Proj | Surplus | There % |
|---|---|---|---|---|
| Patrick Mahomes | QB | 326 | +14 | 81% |
| J.K. Dobbins | RB | 148 | +11 | 54% |
| Travis Kelce | TE | 122 | +8 | 96% |
| Brian Thomas Jr. | WR | 171 | +6 | 49% |
| Jaxson Dart | QB | 318 | +6 | 92% |

Thomas (ESPN 84 vs mock 72) practiced fully Wednesday after a shoulder issue. Pierce (56%) and Metcalf (80%) are the same tier, and Metcalf is still 42% there at 101.

### Pick 101 (R9) — Quarterback if you still don't have one (Mahomes 39%, Dart 75%). Otherwise Kelce as a TE2 only if Bowers' knee worries you; else RB depth.

| Player | Pos | Proj | Surplus | There % |
|---|---|---|---|---|
| Patrick Mahomes | QB | 326 | +14 | 39% |
| Travis Kelce | TE | 122 | +8 | 88% |
| Jaxson Dart | QB | 318 | +6 | 75% |
| RJ Harvey | RB | 142 | +5 | 15% |
| Isaiah Likely | TE | 118 | +4 | 97% |

Picks 116 and 125: nothing left is above replacement except Kelce/Likely/Andrews as TE2s and Kyler Murray (312, 99% there at 116) as a free QB. Use them on the players in §8.

---

## 5. Tiers with cliffs

Built from projection gaps, not rounds. ★ = yours or targeted. ADP shown is ESPN where available.

**Running back** — replacement 137, 34 get started weekly
- **Tier 1 — win the league alone:** Gibbs (DET, 1, 288), Bijan (ATL, 2, 282)
- **Cliff −41.** Both go top-2 in every ESPN draft. Assume gone.
- **Tier 2 — true first-rounders:** Taylor (IND, 5, 241), Cook (BUF, 9, 237), McCaffrey (SF, 7, 234), Achane (MIA, 11, 234), ★ **Chase Brown** (CIN, 10, 230), Barkley (PHI, 14, 229)
- **Cliff −13.**
- **Tier 3 — locked starters:** Henry (BAL, 13, 216), Hampton (LAC, 17, 211), Walker (KC, 16, 210), Kyren (LAR, 25, 203), ★ Breece Hall (NYJ, 38, 203)
- **Cliff −10.** Hall is priced 13 picks after Kyren for the same projection. That's the mispricing at 29.
- **Tier 4 — same tier, four rounds wide:** Javonte (DAL, 30, 193), Jeanty (LV, 22, 191), Etienne (NO, 33, 190), Swift (CHI, 35, 190), Skattebo (NYG, 36, 189), Love (ARI, 32, 188), ★ Irving (TB, 43, 188), Jacobs (GB, 60, 187)
- **Cliff −8.**
- **Tier 5 — committee starters:** Judkins (CLE, 47, 179), Montgomery (HOU, 48, 176), ★ Tuten (JAX, 54, 176), ★ Warren (PIT, 76, 176)
- **Cliff −8.** Warren is the tier's cheapest member by 22 picks.
- **Tier 6 — the dead zone:** Henderson (NE, 71, 168), Stevenson (NE, 68, 166), Pollard (TEN, 73, 164)
- **Cliff −11.**
- **Tier 7 — replacement-adjacent:** Price (SEA, 52, 153), Dowdle (PIT, 77, 153), Dobbins (DEN, 86, 148), Harvey (DEN, 94, 142), Gordon (MIA, 52, 140), Croskey-Merritt (WAS, 103, 137), Hubbard (CAR, 107, 137)

**Wide receiver** — replacement 165, 32 get started weekly
- **Tier 1:** ★ Smith-Njigba (SEA, 6, 268), Chase (CIN, 3, 261), Nacua (LAR, 4, 259)
- **Cliff −16.** Chase (leg hyperextension Aug 25, fine) and Nacua (psoas, returned Aug 30) both carry a draft-week flag; JSN doesn't.
- **Tier 2:** St. Brown (DET, 8, 243), Lamb (DAL, 12, 237), Jefferson (MIN, 15, 231), London (ATL, 20, 227)
- **Cliff −12.**
- **Tier 3 — the ESPN discount tier:** ★ Flowers (BAL, 34, 215), Rice (KC, 23, 214), A.J. Brown (NE, 19, 211), Pickens (DAL, 21, 211), Collins (HOU, 24, 211)
- **Cliff −11.** Flowers goes 11 picks later on ESPN than in mocks; Rice five.
- **Tier 4 — deep and flat, rounds 3–5:** McMillan (CAR, 42, 200), Nabers (NYG, 29, 197 — ACL, Week 1 unconfirmed), Higgins (CIN, 37, 197), ★ Egbuka (TB, 44, 192 — toe), G. Wilson (NYJ, 45, 191), Olave (NO, 28, 189), McConkey (LAC, 39, 189), D. Smith (PHI, 31, 187), Jameson Williams (DET, 56, 187), Adams (LAR, 53, 186)
- **Cliff −6.**
- **Tier 5 — WR3s and flex:** McLaurin (WAS, 57, 180), Odunze (CHI, 61, 180), P. Washington (JAX, 70, 176), ★ Waddle (DEN, 46, 174), Evans (SF, 67, 171), B. Thomas (JAX, 84, 171), DJ Moore (BUF, 50, 169), ★ Burden (CHI, 58, 168), Harrison (ARI, 69, 166), Sutton (DEN, 78, 165), Pierce (IND, 85, 165), Metcalf (PIT, 89, 164)
- **Cliff −8.** Below here is replacement.

**Tight end** — replacement 114, 14 get started weekly
- **Tier 1:** ★ Bowers (LV, 26, 192), McBride (ARI, 27, 184)
- **Cliff −25.** The largest gap on the board after Tier-1 RB. Pay at 20 or skip to Tier 2 at 53.
- **Tier 2:** ★ Loveland (CHI, 41, 159), T. Warren (IND, 55, 151), ★ Pitts (ATL, 74, 150)
- **Cliff −14.**
- **Tier 3 — usable:** Kraft (GB, 72, 136), Fannin (CLE, 66, 133), Kittle (SF, 79, 129), LaPorta (DET, 65, 125), Kelce (KC, 124, 122)
- **Tier 4 — free:** Goedert, Likely, Andrews, Ferguson (114–118)

**Quarterback** — replacement 312, 12 get started weekly
- **Tier 1:** Allen (BUF, 18, 357)
- **Tier 2:** ★ Daniels (WAS, 63, 347), Lamar (BAL, 40, 344), Hurts (PHI, 64, 340)
- **Cliff −9.**
- **Tier 3:** Maye (NE, 51, 331), Burrow (CIN, 49, 329), Mahomes (KC, 104, 326), Prescott (DAL, 59, 324)
- **Cliff −6.**
- **Tier 4 — replacement:** Dart (NYG, 117, 318), Herbert (LAC, 83, 315), C. Williams (CHI, 75, 314), Murray (MIN, 136, 312)

QB1 to QB8 is 33 points — under two a week — which is why the position waits, except for the Daniels/Hurts window at 53 that ESPN pricing creates.

---

## 6. Your guys, pressure-tested

**Bhayshul Tuten (RB, JAX) — proj 176 (cut from 200), +39.**
*Premise:* "gets 60% of the Jaguars' carries." **Wrong.** Liam Coen, Aug 26 (Yahoo): "We're going to have to be a little bit more by committee." Camp settled into a three-back rotation — Tuten on early downs, Chris Rodriguez Jr. (a $10M free agent who played for Coen at Kentucky) between the tackles and at the goal line, LeQuint Allen on third downs (FFC news, Aug 25–Sept 2). Rodriguez had offseason foot surgery, returned to camp July 30 and plans to play Week 1. *The case for:* Coen publicly wants him to "go be special"; camp reports say he took the majority of first-team reps; the team calls him a potential "complete No. 1" (Sept 2). 4.28 speed, and 5 rushing TDs on only 83 carries as a rookie (307 yards, 3.7 YPC; 10 catches). *The risk:* he was sent home sick Sept 2 (expected Week 1), and a 3.7-YPC back sharing goal-line work with a Coen favorite is a 150-point outcome, not 200. *Vegas:* Jaguars 8.5 wins, over −140 — a real offense, not a lot of it his. **Verdict: OK at 53, not before.** He's there 78% at 53 and 0% at 77, but Warren (same 176, 90% at 77) makes him unnecessary.

**Luther Burden III (WR, CHI) — proj 168, +3.**
*Premise:* "3rd in YPRR last year behind Puka and JSN." **True on CBS's measure (2.71, 3rd of 152), not on PFF's (2.34, tied 7th)** — and either way it came on **307 routes**, the fewest of anyone in the top 10 (PFF, July 7). Small samples make YPRR the least stable metric in the hierarchy. *The case for:* the route story improved late — 7.4% target share weeks 1–10, 18.4% weeks 11–17, with a 26.8% target rate per route (Bleacher Nation, Aug 10); DJ Moore is in Buffalo; Ben Johnson says he's "buying Burden stock." *The risk:* Odunze is healthy and Loveland led the team in targets per route (29.1%); Burden's full-season pace from the surge was 105 targets — a WR3, which is exactly his 168. *Vegas:* Bears 9.5, under −125. Caleb Williams' passing-yards prop (3,645) is a featured over, so the volume exists. *ESPN price:* 58 (mock 56) — no discount. **Verdict: PASS at 53 (89% there); he is a round-7 player and gone by 77.** Two names at 53 beat him by 15+ points.

**Emeka Egbuka (WR, TB) — proj 192 (cut from 206), +27.**
*Premise:* "Evans left Tampa." **True** — three-year deal with the 49ers, reported March 9. *The case for:* 127 targets as a rookie (63/938/6 in 17 games), 29.4% first-read target share, 2.49 YPRR in the five weeks before Mayfield's injury wrecked the offense; Godwin is 30 and had 360 yards; the Bucs are moving him to the Z (Fantasy Footballers, July 10; FFC news). *The risk is the one you can see:* sprained toe Aug 12, no preseason snaps, still not in team drills as of Sept 2 — Bowles: "Headed in the right direction. I don't know how fast." That is the metrics reference's "designation in the last week of camp" red flag. I priced roughly a game and a half of missed or limited time. *Vegas:* Bucs 8.5, under −135. **Verdict: NOT BEFORE 44, and only at 44 (80% there, 23% at 53) if he practices fully Friday.** If he's still limited, pass; Irving is the pick there.

**Jaylen Waddle (WR, DEN) — proj 174, +9.**
*Premise:* "Denver threw the most in the league." **True:** Bo Nix threw 612 passes, most in the NFL, and led in dropbacks (680) — at 6.4 yards per attempt, 28th of 33 (DenverSports, Aug 11). Volume is real; efficiency is the question. *The case for:* Denver paid a 1st, 3rd and 4th for him (revealed preference); Payton says he'll "play everywhere except offensive line"; 64/910/6 last year with bad QB play, WR24. Receiving-yards prop 899.5 (Yahoo, Aug 24) — consistent with my 174. *The risk:* Sutton is still the red-zone target, Harvey/Dobbins the checkdowns, and a 14-3 team that just added a receiver is likelier to throw 560 times than 612. Leg strain Aug 5, full pads Aug 18 — healthy now. *ESPN price:* 46 (mock 46). **Verdict: PASS at 44; OK at 53 (30% there) as a WR3 if Daniels and the Tier-4 receivers are gone.**

**Kyle Pitts Sr. (TE, ATL) — proj 150, +36.**
*Premise:* "finished TE2." **True and hollow.** 166.8 half-PPR points was TE2 by total (88/928/5), but TE6 per game (9.8), 86 points behind McBride, and 3 of his 5 TDs came in one game (Week 15: 11/166/3). Check the median week, not the total. *The case for:* Stefanski's Cleveland tight ends were 2nd in the NFL in targets 2020–25; a 3-yr/$54M extension; consensus has him at ~111 targets (Footballguys, July 29). *The risk:* Atlanta still hasn't named a QB — Penix (ACL, Nov 2025) vs Tua; NFL Network says Penix "eventually" (Sept 2). Win total 6.5. *ESPN price:* 74 vs 94 in mocks — 20 picks earlier, so **16% at 77** where the mock says 88%. **Verdict: OK at 53 (86% there) only if you missed both Bowers and McBride at 20 and Loveland at 29; otherwise PASS.** You are drafting him as your TE1 or not at all.

**Colston Loveland (TE, CHI) — proj 159, +45.**
*Premise:* "Ben Johnson loves tight ends." **Half right.** LaPorta's 86-catch rookie year came under Johnson, but Johnson's Lions funneled targets to St. Brown; the better evidence is 2025 itself: Loveland 82 targets/58/713/6 in 16 games (TE12) with the team-high 29.1% target rate per route, while Kmet fell to 48 targets. ESPN projects 118 targets. The depth chart listing him "co-starter" with Kmet (RotoWire, Sept 3) is a formality. *The risk:* year-2 TEs are the classic breakout archetype but Odunze, Burden and Swift all need the ball; 159 is a TE3 projection with no cushion. *ESPN price:* 41 vs 59 in mocks — **80% at 29, 17% at 44.** **Verdict: NOT BEFORE 44 by value, which means realistically PASS** — at 29 he loses to Flowers/Kyren/Hall (+50 to +66 vs +45). The exception: both TE1s gone at 20 (11%); then Loveland at 29 is the pivot and beats waiting for Pitts by nine points.

**Two names to add.** **Jaylen Warren** (RB, PIT, ESPN 76): same 176 as Tuten, 90% at 77, and the sim's most-owned player (88% of runs). **Jameson Williams** (WR, DET, ESPN 56 vs mock 39): 187, 89% at 53 — the biggest ESPN slide among startable receivers; Adams (53) and McLaurin (57) are the same play. And a third, cheaper: **Brian Thomas Jr.** (JAX, ESPN 84): 171, 93% at 77 and 49% at 92.

**Reach rule applied to your picks.** The only endorsed reach is a tight end at 20 (role certainty in a tier that ends before 29). Nobody at 44 or 53 earns a reach: Irving is 71% at 44, Warren 90% at 77, and the receivers at 53 are 86–90% there. Don't take Loveland at 29 or Tuten at 44 for "upside."

---

## 7. Sample drafts and the target build

Across 1,500 ESPN-priced simulations the projected starter total runs **1,772 to 1,906, mean 1,852** (sd 22); nine of the ten sample drafts land within 35 points of each other — two a week — which is the message: structure (Brown kept, TE at 20, Flowers or a back at 29) matters more than any single mid-round name.

**Most-owned across 1,500 runs (picks 1–8):** Jaylen Warren 88%, Jayden Daniels 60%, Zay Flowers 55%, Brock Bowers 51%, McMillan 50%, Breece Hall 47%, Smith-Njigba 42%, McBride 32%, Dobbins 29%, Brian Thomas 23%.

**What happened in essentially every draft:** a Tier-1 tight end at 20 (8 of 10); Warren at 77 (8 of 10); Flowers at 29 or 20 (5 of 10); a QB at 44–53 in seven and Mahomes at 92 in the other three — never later, because nothing is left; K/DEF never before 164. The sim's own weakness: it filled WR2 with Pittman (150) or Metcalf (164) from picks 101–125 in five drafts — which is why 53 and 92 carry the WR insurance below.

**The target build** (every pick ≥ 45% reachable unless noted):

| Pick | Player | Pos | Proj | There % |
|---|---|---|---|---|
| KEEP | Chase Brown | RB | 230 | — |
| 5 | Jaxon Smith-Njigba | WR | 268 | 63% |
| 20 | Brock Bowers (McBride) | TE | 192 (184) | 52% (72%) |
| 29 | Zay Flowers | WR | 215 | 85% |
| 44 | Bucky Irving (Jacobs) | RB | 188 (187) | 71% (60%) |
| 53 | Jayden Daniels (Jameson Williams) | QB (WR) | 347 (187) | 47% (89%) |
| 77 | Jaylen Warren | RB | 176 | 90% |
| 92 | Brian Thomas Jr. (Mahomes) | WR (QB) | 171 (326) | 49% (81%) |
| 101 | Kelce / Dart / RJ Harvey | TE / QB / RB | — | 88 / 75 / 15% |
| 116–149 | see §8 | | | |
| 164 | Kicker (McLaughlin / Little) | K | 136–139 | 52% / 34% |
| 173 | Defense (Baltimore / Buffalo) | DEF | 103 | 82% / 99% |

Starters: Daniels 347 · Brown 230 · Irving 188 · JSN 268 · Flowers 215 · Bowers 192 · Warren 176 (flex) · K 139 · DEF 103 = **1,858**, right at the sim mean with every piece at least a coin flip.

**Why this one.** It spends the two steep-surplus picks (5 and 20) on the two positions with the biggest cliffs, buys the receiver the room under-prices at 29, and takes backs at 44 and 77 where ESPN drafts them on time.

**The honest weakness:** RB2. Irving is a committee back off a 3.4-YPC season and Warren is a timeshare; if Irving is gone at 44 (29%), Jacobs (60%) is the same tier, and only if both are gone do Judkins/Montgomery cost 9–12 points. **The hedge:** if Kyren Williams is there at 29 (31%), take him over Flowers and McMillan at 44 (66%) — 203 + 200 instead of 215 + 188, and the RB2 problem disappears at zero cost.

**The upside case, not the plan:** Bijan at 5 (21%) + Bowers + Flowers + Hall-if-he-falls-to-44 (23%) projects about 1,900. Don't build for it.

---

## 8. The late-round plan (picks 101–173)

- **Handcuffs.** Kenny Gainwell for Irving (83% at 92, 47% at 101); Braelon Allen if you drafted Hall (74% at 101). Samaje Perine, Brown's backup, isn't in the pool and won't be drafted — claim him Week 1; he is the one handcuff that matters.
- **Second-year and rookie volume paths at 116–149:** Kyle Monangai (CHI, 82% at 101), KC Concepcion (CLE, 85% at 116), Carnell Tate (TEN, 34% at 101), Tre Tucker (LV, 84% at 149), Makai Lemon (PHI, 77% at 149).
- **Next-year keeper logic.** Waiver pickups can't be kept, so a round-11+ hit is the only cheap keeper you can manufacture. Bias 125–149 toward Jordyn Tyson (NO, 100% at 149), Travis Hunter (JAX, 100% at 173 — the draft ends before ADP reaches him), Mike Washington (LV, Jeanty's fill-in, 61% at 149), Tank Bigsby (PHI, 75% at 173). A Tyson or Hunter breakout is a round-13 keeper in 2027.
- **QB2** only if Daniels/Hurts is your QB1 — Dart at 101 (75%) or Kyler at 116 (99%).
- **K and DEF at 164 and 173.** The room starts on kickers and defenses in round 11; Seattle, Denver and Houston are gone by 140, and Baltimore (82%) or Buffalo (99%) is there at 173. McLaughlin (52%) or Little (34%) at 164. Brandon Aubrey (+25 over K12) is gone by 149 (25%); he would cost pick 140 (54%), which is too much for 1.5 a week.

---

## 9. Assumptions worth checking before you commit

- **Keeper rule:** same-round, Brown at round 6, waiver pickups not keepable. If any of those is wrong, re-read §1.
- **Lineup:** 12 teams, one flex, no superflex. A superflex slot would make Daniels the keeper conversation.
- **15 rounds including K/DEF:** anyone with an ADP past ~155 goes undrafted, which is why the round-14/15 lottery tickets are free.
- **ESPN pricing covers the top 100 only** (Footballguys ESPN column); players 101+ carry mock ADP, so There % past pick 100 is approximate.
- **The one assumption that flips the board:** the 28-point RB-vs-WR replacement gap. If my tier-3/4 receiver projections are 8–10% low (the ESPN room's receiver discount is wrong and the mocks are right), Flowers at 29 is clearly right and Irving at 44 becomes McMillan. If the backs are the ones under-projected, take Kyren/Hall at 29 without hesitation. Decide which side you're on before Sunday, not during.
- **Injury flags to re-check Saturday:** Flowers (lower body), Egbuka (toe), Nabers (ACL), Jeanty (ankle), Tuten (sent home sick Sept 2), Nacua (psoas), Chase (leg), Hall (groin), Henderson (ankle). A "did not practice Friday" changes the pick.
- Real leaguemates are less rational than simulated ones. The two who "always take a QB by round 4" push the QB run earlier than ESPN ADP says: Daniels at 53 is less likely than 47%, and the receivers at 53 more likely than 89%.

---

## Appendix

**Terms.** *Replacement level* — points of the worst player at a position who still has to start for someone every week. *Surplus* — projection minus replacement; the number every table is sorted by. *There %* — how often the player was still undrafted at that pick across the simulated drafts. *Tier / cliff* — players close enough in projection that the choice barely matters / the point drop between tiers. *Keeper inflation* — with keepers removed, the player available at pick p is worse than ADP p suggests. *Route share, target share, TPRR, YPRR* — share of team pass plays run as routes; share of targets; targets per route; yards per route (unstable under ~250 routes). *Win total* — the sportsbook line on a team's wins, used as a game-script prior.

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

**Simulation settings.** 1,500 runs, seed 1000; keepers drawn (weighted toward better players, rounds correlated to quality — the league hasn't published its list); opponents draft ADP + noise scaled to each player's spread and capped at 0.2 × ADP + 4, with a positional-need bias from round 8 and kickers/defenses on a rising curve from round 11; "me" weighs the opportunity cost of waiting at each position; replacement ranks QB12 / RB34 / WR32 / TE14 / K12 / DEF12; my keeper Chase Brown, round 6. Net keeper inflation measured in-sim: +11.2 picks at 5, +7.9 at 20, +6.1 at 29, +3.9 at 44, +2.9 at 53, +0.5 at 77, +0.1 at 92. A 400-run keeper-free pass priced the keeper table. The mock-ADP comparison figures in §3 come from the same simulator run on `players_mock-adp.csv`.

**Assumptions.** Lineup as configured; injuries baked into expected games rather than modeled separately; K/DEF treated as near-interchangeable and drafted last; players not in `players.csv` (e.g., Samaje Perine, Sean Tucker) are waiver-wire, not draft, targets.
