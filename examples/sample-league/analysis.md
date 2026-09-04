# Replacement Level — 2026 draft analysis

**League:** The Sample League · ESPN · 12 teams · snake, pick 5 · half-PPR, 4-pt pass TD, −2 INT · 1 QB / 2 RB / 2 WR / 1 TE / 1 FLEX / K / DEF · one keeper at original round
**Draft:** Sunday, September 6, 2026 · **Written:** Thursday, September 3, 2026 (regenerated September 4 on the v2.1 rollout engine — every pick ranked by the starting lineup it leaves you with, not by surplus)
**Projections:** mine (built Sept 3, scored in this league's system). **ADP:** ESPN column of the Footballguys table for the top 100, FantasyFootballCalculator half-PPR mocks Aug 28–Sep 2 for the spread and for everyone deeper. **Simulation:** 1,500-run availability Monte Carlo plus 200 draft rollouts per pick; the full name × pick matrix is in `sim_availability.csv`.

---

## 1. Verdict: keep Chase Brown

Not close, and the verdict is in the same unit as the rest of the page: the starting lineup you finish with.

### The verdict in lineup points

Full drafts simulated 1,000 times per scenario — you drafting sensibly, the room off ESPN ADP, twelve keepers drawn, the keeper's round forfeited:

| Scenario | Cost | Projected starting lineup | SE | vs. best |
|---|---|---|---|---|
| **Keep Chase Brown** | R6 → pick 68 | **1,864** | ±0.6 | — |
| Keep Jayden Daniels | R7 → pick 77 | 1,827 | ±0.8 | −37 |
| Keep Brock Bowers | R3 → pick 29 | 1,824 | ±0.8 | −40 |
| Keep Tetairoa McMillan | R5 → pick 53 | 1,813 | ±1.0 | −51 |
| Keep nobody | — | 1,810 | ±0.9 | −54 |

**Brown is worth 54 points of starting lineup over keeping nobody — 3.2 a week for one round-6 pick.** No other candidate is worth a third of that; Daniels and Bowers are level with each other and both forty behind Brown. Only the four candidates with positive isolated surplus got a scenario run, and these totals come from their own free-running pass — **not** the scale of the pick values in §4 or the plan total in §7. §2 explains why, and it matters more than it used to.

### The keeper math, as the explanation

Your picks at slot 5: 5, 20, 29, 44, 53, **68 (forfeited for Brown)**, 77, 92, 101, 116, 125, 140, 149, 164, 173. Surplus in points — the keeper's points over the last startable player at his position, minus what the best player available at that pick would have returned — ranks nothing; it says *why* the scenario table came out as it did.

| Player | Cost | You pay (pick) | ESPN ADP | Proj | Surplus (picks) | Surplus (points) | Verdict |
|---|---|---|---|---|---|---|---|
| **Chase Brown** (RB) | R6 | 68 | 10 | 230 | +58 | **+35** | Keep |
| Brock Bowers (TE) | R3 | 29 | 26 | 192 | +3 | +15 | No — the board hands you a tight end at 53 |
| Jayden Daniels (QB) | R7 | 77 | 63 | 347 | +14 | +9 | No — re-draft him at 44 |
| Tetairoa McMillan (WR) | R5 | 53 | 42 | 200 | +11 | +8 | No |
| Drake London (WR) | R2 | 20 | 20 | 227 | 0 | −3 | No — he *is* your pick 20 |
| Courtland Sutton (WR) | R8 | 92 | 78 | 165 | +14 | −16 | No |
| Travis Etienne Jr. (RB) | R4 | 44 | 33 | 190 | +11 | −17 | No |
| Jaylen Warren (RB) | waiver | — | 76 | 176 | — | — | Not keepable |

Note how badly the "picks of value" column lies: Sutton shows +14 picks and is a −16 keeper; Bowers +3 picks and is +15. Pick 92 and pick 29 are different currencies.

### Why Brown, beyond the number

- **Keeper inflation is front-loaded and gone by the pick he costs.** Twelve keepers leave the pool and twelve picks are forfeited: in-sim, pick 5 buys roughly the ADP-16 player (+11.2), 20 the ADP-28 player (+7.9), 29 +6.1, 44 +3.9, 53 +2.9, and by 77 it is half a pick. **Pick 68 buys a true round-6 player; Brown is a round-1 player.** That is the whole trade.
- **The player.** 1,019 rushing yards, a Bengals-record 69 catches for 437, 11 touchdowns in 2025; 18.2 touches and 100 yards a game from Week 6 on (Bengals.com, June 25). 69% of preseason-opener snaps to Perine's 31%. Burrow back, no holdout, no injury news.
- **The honest bear case.** Sharp Football (Aug 31) quotes **824.5 rushing yards (−110)** and **5.5 rushing TDs (−125)** — 210–220 points in this scoring, not 230 — and the Bengals' 10.5 win total has the under favoured. Knock fifteen off and he is still your largest keeper edge by more than thirty.

### The one thing you must confirm first

That the commissioner's sheet lists Brown at **round 6** and the league is same-round, not round-minus-one. Round-minus-one costs pick 53 instead of 68: you lose the tight-end slot in the plan and the verdict narrows, but it is still the keep by a wide margin. Also confirm **waiver pickups are not keepable** — Jaylen Warren came off waivers and would be a valuable second keeper at a last-round cost in a league that allowed it.

### Why not the tempting alternatives

**Brock Bowers (R3, −40):** at pick 20 he and Drake London are 0.3 points apart — the same lineup — and Pitts is 85% available at 53. **Jayden Daniels (R7, −37):** the plan's pick at 44 at 81% availability, so paying pick 77 for him is a swap you already win. **Tetairoa McMillan (R5, −51):** 88% at 29, 65% at 44, 8 points behind the pick at 44. **Drake London (R2, −3 on surplus):** keeping a player at the exact pick where he is the correct selection buys nothing.

### What you sacrifice by keeping nobody

Pick 68 buys the Warren / Henderson / Stevenson band — 164 to 176 points, a replacement-level starting back. Handing back 54 points of starting lineup for a fifteenth roster spot is dominated.

## 2. How every number on this page was produced

For each of your picks, each of up to eight candidates (plus every player you named) was **planted at that pick and the rest of the draft simulated 200 times** — the room off ESPN ADP with noise, you drafting sensibly afterwards — and the best legal starting lineup scored. **Pick value** is that projected lineup; the gap below the top row is what the alternative costs you. Three details make it mean something. **Common random numbers:** every candidate branches from the same drafts, so the differences are about the players. **A matched control arm:** a player who falls to you one draft in five only falls when the whole board fell, so each sample is also played out with nobody forced in and the candidate is scored on the *difference* he makes on his own samples (`control`, `vs_control`). **Noise:** two candidates inside about two standard errors are not distinguishable, and this page says "level" rather than picking a winner on a decimal. The rollouts run through round 9.

### What a pick value is not

**Pick values are comparable within a pick and not across picks.** Each is measured against *that pick's own control arm*, which already assumes you followed the plan to get there, so the column drifts downward as the draft goes on. A 1,858 at pick 5 and a 1,839 at pick 101 are not your team declining; they are two different baselines. Never subtract one pick's value from another's, and never read one against a keeper-scenario total — those come from a free-running policy on their own pass, a third scale again.

### The limit worth arguing with: the plan loses to no plan

Follow the plan in §7 and the simulation gives **1,839**. Let the same drafter choose freshly at every pick with the same heuristic — the rollouts' own control arm at pick 5 — and it gives **1,863**. **The tool's recommendation trails the tool's own default by 24 points, about a point and a half a week.** The keeper table's free-running 1,864 is that policy on a separate pass landing in the same place, so the 24 points are real, not a scaling artifact. Two causes, one benign:

- A plan is a ranking computed *before* the draft, and someone reacting to the actual board does a little better. That is the price of having a plan at all, and the board recovers most of it by being adaptive: take the top row **still on the board**, which is the policy the 1,839 already simulates.
- The rest-of-draft policy inside a rollout is that same heuristic. Force in a player it would not have taken and it must repair a roster shape it did not plan — imperfectly — so the candidate is charged for the policy's rigidity as well as his own merits. That biases the engine against exactly the picks where the rollouts disagree most interestingly with the heuristic. **It is the first thing to fix in a v2.1, and until it is fixed this page overstates what the plan is worth.**

The ranking and the within-pick gaps survive it. Treating 1,839 as a promise does not.

**Replacement level, for context rather than for decisions:**

| Pos | Replacement | Who that is |
|---|---|---|
| QB | 312 | QB12 (Kyler Murray) |
| RB | 164 | RB28 (Tony Pollard) |
| WR | 156 | WR35 (Christian Watson) |
| TE | 116 | TE13 (Mark Andrews) |
| K | 130 | K12 |
| DEF | 101 | DEF12 |

By flex equilibrium: dedicated slots first, then the twelve flex and three bye slots to the best remaining player regardless of position. They fill **4 RB / 11 WR / 0 TE**, the one-glance statement that the receiver pool is deeper. Move the running-back baseline three ranks and every back gains or loses sixteen points of surplus at once — which under v1 moved the plan and now moves nothing, because a final lineup involves no baseline at all.

## 3. Pick geometry and the cost of waiting

Ladder with the keeper round removed: **5 · 20 · 29 · 44 · 53 · 77 · 92 · 101 · 116 · 125 · 140 · 149 · 164 · 173.** Slot 5 is a middle slot — no paired turn, picks alternating 15 and 9 apart — so every player whose ADP sits between two of your picks is a now-or-never decision, and the 15-pick gaps (5→20, 29→44, 53→77) are where tiers vanish. Net keeper inflation, in-sim: **+11.2 picks at 5, +7.9 at 20, +6.1 at 29, +3.9 at 44, +2.9 at 53, +0.5 at 77, +0.1 at 92, zero at 101.**

### What waiting costs at each of your picks

Points of value lost by waiting until your next turn (`cost_of_waiting`, computed to the same depth the board renders — through pick 101). The bold cell is the position about to run out.

| Pick | QB | RB | WR | TE |
|---|---|---|---|---|
| 5 | 7 | **47** | 38 | 5 |
| 20 | 2 | 6 | 11 | **22** |
| 29 | 1 | 10 | **16** | 11 |
| 44 | 4 | **11** | 8 | 3 |
| 53 | 16 | 6 | 16 | **17** |
| 77 | 3 | **27** | 7 | 10 |
| 92 | 2 | 9 | **12** | 0 |
| 101 | 6 | **11** | 6 | 2 |

**Reading it.** Running back drains fastest at your first pick (47 points, the largest cell on the board) and again at 77 (27): the first is Gibbs, Bijan and Taylor leaving the room, the second is the last turn at which a startable back exists at all. Tight end has exactly two windows, 22 at pick 20 and 17 at 53, and is flat everywhere else. Quarterback never costs more than seven until 53, where it jumps to 16 because Daniels, Hurts, Maye and Burrow all clear the board between 53 and 77 — so the quarterback comes at 44 or 53 and cannot come later. Receiver costs 38 at pick 5 and then sits between 6 and 16 all draft, which is what a deep position looks like. The table is unaffected by where replacement level is drawn: the same baseline sits in both terms and cancels. Where it disagrees with §4 — it says back, §4 says receiver — the rollouts win, because they measured a lineup: 47 points is how far the *best available back* falls, not an instruction to take Jonathan Taylor when you already have Chase Brown.

## 4. The board — top five at each pick

Ranked by **pick value**: the projected lineup if you take that player here and draft sensibly afterwards. **Now** reads against the player this pick recommends, who leads the table: **TAKE** on him, a positive number on anyone worth more if he fell to you, a negative number on anyone worth less (≈ = level with him, inside the noise band). **Here** and **Next** are availability at this pick and the following one, with your own seat drafting off ADP, so the number is about the room. Plan B is the next row down you can actually get; a better player who rarely falls is listed as upside instead.

### Pick 5 (R1) — Wide receiver. Bijan Robinson if he fell (21%). Otherwise Jaxon Smith-Njigba.

| Player | Pos | Proj | Pick value | Now | Here | Next |
|---|---|---|---|---|---|---|
| Jaxon Smith-Njigba | WR | 268 | 1,858 | TAKE | 63% | 0% |
| Bijan Robinson | RB | 282 | 1,862 | +4 | 21% | 0% |
| Ja'Marr Chase | WR | 261 | 1,852 | −6 | 31% | 0% |
| Puka Nacua | WR | 259 | 1,850 | −8 | 40% | 0% |
| Jonathan Taylor | RB | 241 | 1,835 | −22 | 52% | 0% |

Gibbs is gone before your pick in 86% of drafts, Bijan in 79%: Bijan is genuinely the best pick, four clear and outside the noise, but one time in five is upside, not a plan. **Plan B is Ja'Marr Chase at −5.6, not Jonathan Taylor** — a fallback you often can't get beats one that costs twenty points, and Nacua sits two behind Chase. Chase's leg and Nacua's psoas are draft-week flags JSN does not carry. The sixth row, Amon-Ra St. Brown, produces the *same lineup* as Taylor: with Brown kept, your second back is a bench problem you solve at 77 for free.

### Pick 20 (R2) — Wide receiver or tight end, whichever is there. London and Bowers are level; take London if both are.

| Player | Pos | Proj | Pick value | Now | Here | Next |
|---|---|---|---|---|---|---|
| Drake London | WR | 227 | 1,861 | TAKE | 62% | 1% |
| Brock Bowers | TE | 192 | 1,861 | −0.3 ≈ | 50% | 8% |
| Trey McBride | TE | 184 | 1,856 | −5 | 71% | 20% |
| Rashee Rice | WR | 214 | 1,849 | −12 | 79% | 12% |
| Nico Collins | WR | 211 | 1,847 | −14 | 80% | 20% |

London and Bowers are the two names level with the best, three tenths apart, so the tiebreak is availability: 62% against 50%, and neither survives to 29. Take London if both are there and let the tight end come at 53 — the biggest change from the v1 board, which read "Tight end. Bowers if he's there." Waiting from 20 to 29 costs 22 points, but Pitts is 85% available at 53: the lineup cannot tell Bowers-at-20-plus-a-receiver-at-53 from a-receiver-at-20-plus-Pitts-at-53. Zay Flowers is the sixth row and loses by 15 because he is 85% there at 29.

### Pick 29 (R3) — Wide receiver. Zay Flowers (85%). Trey McBride if he fell (20%).

| Player | Pos | Proj | Pick value | Now | Here | Next |
|---|---|---|---|---|---|---|
| Zay Flowers | WR | 215 | 1,858 | TAKE | 85% | 5% |
| Trey McBride | TE | 184 | 1,854 | −4 | 20% | 0% |
| Nico Collins | WR | 211 | 1,852 | −6 | 20% | 0% |
| Breece Hall | RB | 203 | 1,850 | −8 | 88% | 34% |
| Kyren Williams | RB | 203 | 1,850 | −8 | 28% | 0% |

Flowers is alone at the top: McBride at −3.8 sits just outside the band, as close to a coin flip as the arithmetic will admit, and he is the Plan B — 0% at 44, so take him if he lasts. Flowers is the pick *here* rather than at 20 because he is 87% at 20, 85% at 29 and 5% at 44: one turn, not two. WR7 in half-PPR last year (86 / 1,211 / 5, 55.9% of Ravens WR targets), on the joint-highest win total, eleven picks cheaper on ESPN than in mocks — but out of team drills Sept 1–2. If he is doubtful, Tetairoa McMillan is the sixth row at −13 and survives to 44 two-thirds of the time.

### Pick 44 (R4) — Quarterback. Jayden Daniels (81%). Breece Hall if he falls (34%).

| Player | Pos | Proj | Pick value | Now | Here | Next |
|---|---|---|---|---|---|---|
| Jayden Daniels | QB | 347 | 1,852 | TAKE | 81% | 57% |
| Breece Hall | RB | 203 | 1,858 | +6 | 34% | 0% |
| Bucky Irving | RB | 188 | 1,848 | −4 | 73% | 13% |
| Josh Jacobs | RB | 187 | 1,848 | −4 | 57% | 27% |
| Jalen Hurts | QB | 340 | 1,847 | −5 | 82% | 64% |

The pick that moved most between engines: under v1 the quarterback waited until 53. Cost of waiting says four points, but that measures the *best available* quarterback, and Daniels specifically is 81% here and 57% at 53 — Daniels if he is there, Hurts (five behind, 82%) if not, and the position closes before the 16-point cliff at 53. Hall is the best pick value at any pick after 20; taking him moves the quarterback to 53 and the tight end to 77 (Pitts 18%), which is where the plan leaks. Bucky Irving is the Plan B at 3.7 behind Daniels and, unlike on the v1 board, is **not** level with him: 3.7 against a combined band of 2.6.

### Pick 53 (R5) — Tight end, and round 5 is a shrug. Kyle Pitts Sr. (85%), level with Tyler Warren (70%). Josh Jacobs if he falls (27%).

| Player | Pos | Proj | Pick value | Now | Here | Next |
|---|---|---|---|---|---|---|
| Kyle Pitts Sr. | TE | 150 | 1,847 | TAKE | 85% | 18% |
| Josh Jacobs | RB | 187 | 1,847 | +0.5 ≈ | 27% | 0% |
| Tyler Warren | TE | 151 | 1,847 | −0.1 ≈ | 70% | 0% |
| Bucky Irving | RB | 188 | 1,846 | −1 ≈ | 13% | 0% |
| Emeka Egbuka | WR | 192 | 1,846 | −1 ≈ | 23% | 0% |

**Six names are level with the best: Jacobs, Pitts, Tyler Warren, Irving, Egbuka and Garrett Wilson** (the sixth row, −4, 35%). Say it plainly — round 5 is a shrug: the table spans 4.9 points on standard errors of 0.9 to 2.5, and staring at 1,846.9 against 1,846.8 will not rank it. So it is a roster decision, and the roster says tight end — you have none, waiting costs 17 points, Pitts is 18% at 77 and Tyler Warren 0%, while a third back sits on your bench. **Take the tight end**: Pitts at 85% over Tyler Warren at 70%, either one the same pick. Jacobs (27%) and Irving (13%) are worth taking if the board hands them to you, buying the tight end at 77 instead.

### Pick 77 (R7) — Running back. Jaylen Warren (90%). Rhamondre Stevenson or TreVeyon Henderson if he is gone.

| Player | Pos | Proj | Pick value | Now | Here | Next |
|---|---|---|---|---|---|---|
| Jaylen Warren | RB | 176 | 1,843 | TAKE | 90% | 13% |
| Rhamondre Stevenson | RB | 166 | 1,839 | −4 | 49% | 0% |
| TreVeyon Henderson | RB | 168 | 1,839 | −4 | 64% | 1% |
| Tony Pollard | RB | 164 | 1,838 | −5 | 80% | 3% |
| Brian Thomas Jr. | WR | 171 | 1,836 | −7 | 92% | 48% |

The clearest pick on the board and the only one where the top row stands alone: Warren is 90% available and 3.7 clear, and this is the last turn where a startable second back exists — the 27-point cost-of-waiting cell says so, and every back above him is gone by 92. Brian Thomas Jr. is the sixth-best option and costs seven points purely because he is 48% at 92 while Warren is 13%. Warren splits carries with Rico Dowdle, which is why he projects 176 and not 205; the simulator takes him in 87% of drafts anyway.

### Pick 92 (R8) — Wide receiver. Alec Pierce (55%). Brian Thomas Jr., DK Metcalf and Courtland Sutton are level with him.

| Player | Pos | Proj | Pick value | Now | Here | Next |
|---|---|---|---|---|---|---|
| Alec Pierce | WR | 165 | 1,842 | TAKE | 55% | 11% |
| Brian Thomas Jr. | WR | 171 | 1,842 | 0.0 ≈ | 48% | 8% |
| DK Metcalf | WR | 164 | 1,841 | −1 ≈ | 80% | 40% |
| Courtland Sutton | WR | 165 | 1,841 | −1 ≈ | 12% | 0% |
| Michael Wilson | WR | 148 | 1,840 | −2 | 95% | 92% |

Four names are level with the best — Thomas, Pierce, Metcalf and Sutton — spanning 0.9 points on standard errors of 0.4 to 0.9. **Pierce is the plan's pick on availability, not points:** Thomas leads on raw pick value but is there 48% of the time, under the plan's 50% floor, and Pierce is 55%. Metcalf at 80% is the safest and 40% at 101, so he can wait a round; Sutton is a 12% lottery. The tie exists because ESPN prices Metcalf at 89 and Pierce at 85 against mock ADPs of 64 and 63 — the largest slide on the board, and what puts three startable receivers in your round 8.

### Pick 101 (R9) — Running back, and this is a coin flip. Chuba Hubbard (93%). Eight names are level.

| Player | Pos | Proj | Pick value | Now | Here | Next |
|---|---|---|---|---|---|---|
| Chuba Hubbard | RB | 137 | 1,839 | TAKE | 93% | 54% |
| RJ Harvey | RB | 142 | 1,840 | +1 ≈ | 17% | 0% |
| J. Croskey-Merritt | RB | 137 | 1,839 | 0.0 ≈ | 70% | 14% |
| Kenny Gainwell | RB | 134 | 1,839 | −0.1 ≈ | 50% | 3% |
| Kyle Monangai | RB | 132 | 1,838 | −0.1 ≈ | 83% | 31% |

**Eight players are level with the best — the five above plus Michael Pittman Jr., Michael Wilson and DK Metcalf — and the whole table spans 1.9 points.** Write that down instead of the ordering: anyone who tells you Harvey is 0.9 better than Hubbard is reading noise. Take the back with the clearest path to volume and the best chance of being there — Hubbard at 93%. Croskey-Merritt (70%) is the same pick, Harvey the same pick when he falls (17%), and if you already have three backs so is Pittman at 100%.

Picks 116 and beyond are past the rollout horizon; see §8.

## 5. Tiers with cliffs

Built from projection gaps, not rounds. The right-hand number is **vs. free** — projection minus replacement level; it shows which positions are deep and does not rank the picks above. ★ = yours or targeted, ADP is ESPN where available, and the board carries the full lists.

**Running back** — replacement 164, 28 get started weekly
- **Tier 1, win the league alone:** Jahmyr Gibbs (DET, 1, 288, +124), Bijan Robinson (ATL, 2, 282, +118)
- **Cliff −41,** the largest gap at any position. Gibbs gone before pick 5 in 86% of drafts, Bijan in 79% — and Bijan at 5 is the best pick value on your board, one time in five.
- **Tier 2, the only backs worth a first-round pick:** Jonathan Taylor (IND, 5, 241, +77), James Cook III (BUF, 9, 237, +73), Christian McCaffrey (SF, 7, 234, +70), De'Von Achane (MIA, 11, 234, +70), ★ **Chase Brown** (CIN, 10, 230, +66), Saquon Barkley (PHI, 14, 229, +65) — all gone before pick 20
- **Cliff −13.** Brown at a round-6 cost is this tier for free — the entire reason the rest of the board leans receiver.
- **Tier 3, starters:** Derrick Henry (BAL, 13, 216, +52), Omarion Hampton (LAC, 17, 211, +47), Kenneth Walker (KC, 16, 210, +46), Kyren Williams (LAR, 25, 203, +39), ★ Breece Hall (NYJ, 38, 203, +39)
- **Cliff −10.** Hall is the tier's outlier by price: 88% at 29, 34% at 44, best pick value at 44 when he falls.
- **Tier 4, committee backs:** Javonte Williams (DAL, 30, 193, +29), Ashton Jeanty (LV, 22, 191, +27), Travis Etienne Jr. (NO, 33, 190, +26), Bucky Irving (TB, 43, 188, +24), ★ Josh Jacobs (GB, 60, 187, +23)
- **Cliff −8.** Irving (73%) and Jacobs (57%) are the only two who reach 44; Jacobs is also the top row at 53 when he lasts.
- **Tier 5, your RB2 tier:** Quinshon Judkins (CLE, 47, 179, +15), David Montgomery (HOU, 48, 176, +12), ★ Bhayshul Tuten (JAX, 54, 176, +12), ★ Jaylen Warren (PIT, 76, 176, +12)
- **Cliff −8.** Three identical 176 projections across 29 picks of ADP. **This is where the value is:** Warren is 90% at 77, Tuten 0%.
- **Tier 6, replacement:** TreVeyon Henderson (NE, 71, 168, +4), Rhamondre Stevenson (NE, 68, 166, +2), Tony Pollard (TEN, 73, 164, +0)
- **Cliff −11.** Below here it is bench depth: RJ Harvey (142, −22), ★ J. Croskey-Merritt (137, −27), ★ Chuba Hubbard (137, −27), Kenny Gainwell (134, −30), Kyle Monangai (132, −32).

**Wide receiver** — replacement 156, 35 get started weekly
- **Tier 1:** ★ Jaxon Smith-Njigba (SEA, 6, 268, +112), Ja'Marr Chase (CIN, 3, 261, +105), Puka Nacua (LAR, 4, 259, +103)
- **Cliff −16.** JSN is 63% at pick 5 and the only one without a draft-week flag; Chase is the Plan B there at 31%.
- **Tier 2:** Amon-Ra St. Brown (DET, 8, 243, +87), CeeDee Lamb (DAL, 12, 237, +81), Justin Jefferson (MIN, 15, 231, +75), ★ Drake London (ATL, 20, 227, +71)
- **Cliff −12.** London is 62% at 20 — the tier's last member and the one an ESPN room lets slide to your second pick.
- **Tier 3, the ESPN discount tier:** ★ Zay Flowers (BAL, 34, 215, +59), Rashee Rice (KC, 23, 214, +58), A.J. Brown (NE, 19, 211, +55), George Pickens (DAL, 21, 211, +55), Nico Collins (HOU, 24, 211, +55)
- **Cliff −11.** Flowers goes eleven picks later on ESPN than in mocks and is 85% at 29 while the other four are 1–20%. That gap is the plan.
- **Tier 4, deep and flat:** ★ Tetairoa McMillan (CAR, 42, 200, +44), Tee Higgins (CIN, 37, 197, +41), Malik Nabers (NYG, 29, 197, +41 — ACL), ★ Emeka Egbuka (TB, 44, 192, +36 — toe), Garrett Wilson (NYJ, 45, 191, +35), Ladd McConkey (LAC, 39, 189, +33), plus Olave, DeVonta Smith, Jameson Williams and Davante Adams
- **Cliff −6.** Ten receivers inside 14 points across 28 picks of ADP. None is the pick at 44; Egbuka and Garrett Wilson are level with the best at 53, which tells you how flat round 5 is, not how good they are.
- **Tier 5, WR4 and flex:** Terry McLaurin (WAS, 57, 180, +24), Rome Odunze (CHI, 61, 180, +24), ★ Jaylen Waddle (DEN, 46, 174, +18), ★ Brian Thomas Jr. (JAX, 84, 171, +15), ★ Luther Burden III (CHI, 58, 168, +12), Courtland Sutton (DEN, 78, 165, +9), ★ Alec Pierce (IND, 85, 165, +9), ★ DK Metcalf (PIT, 89, 164, +8)
- **Cliff −8.** Christian Watson (156) is replacement. Pierce, Sutton and Metcalf are priced twenty-plus picks below the mock market on ESPN — why four names are level at pick 92.

**Tight end** — replacement 116, 13 get started weekly
- **Tier 1:** ★ Brock Bowers (LV, 26, 192, +76), Trey McBride (ARI, 27, 184, +68)
- **Cliff −25.** The clearest case of surplus and pick value disagreeing: Bowers is +76 vs. free and London +71, and at pick 20 they are level — because tier 2 is 85% available at your fifth pick.
- **Tier 2:** ★ Colston Loveland (CHI, 41, 159, +43), Tyler Warren (IND, 55, 151, +35), ★ Kyle Pitts Sr. (ATL, 74, 150, +34)
- **Cliff −14.** Loveland 82% at 29, 15% at 44; Tyler Warren 70% at 53, 0% at 77; Pitts 85% at 53, 18% at 77 — and nineteen picks of ADP cheaper.
- **Tier 3, usable:** Tucker Kraft (GB, 72, 136, +20), Harold Fannin Jr. (CLE, 66, 133, +17), George Kittle (SF, 79, 129, +13), Travis Kelce (KC, 124, 122, +6)
- **Tier 4, free:** Dallas Goedert (118, +2), Isaiah Likely (118, +2), Mark Andrews (116, +0), Jake Ferguson (114, −2)

**Quarterback** — replacement 312, 12 get started weekly
- **Tier 1:** Josh Allen (BUF, 18, 357, +45) — 13% at pick 20, gone by 29. Not your problem.
- **Tier 2, the window:** ★ Jayden Daniels (WAS, 63, 347, +35), Lamar Jackson (BAL, 40, 344, +32), Jalen Hurts (PHI, 64, 340, +28)
- **Cliff −9.** Daniels 81% and Hurts 82% at 44, both under 1% at 77.
- **Tier 3:** Drake Maye (NE, 51, 331, +19), Joe Burrow (CIN, 49, 329, +17), Patrick Mahomes (KC, 104, 326, +14), Dak Prescott (DAL, 59, 324, +12)
- **Tier 4, replacement:** Jaxson Dart (NYG, 117, 318, +6), Justin Herbert (LAC, 83, 315, +3), Kyler Murray (MIN, 136, 312, +0)

QB1 to QB8 is 33 points, under two a week. What makes the position a round-4 pick is not the top of it but the shape of the exit: Daniels, Hurts, Maye and Burrow are all above 70% at 44 and under 1% at 77 — no gradual decline, just a wall between your fourth and seventh picks.

## 6. Your guys, pressure-tested

**Bhayshul Tuten (RB, JAX) — proj 176, +12 vs. free.**
*Premise:* "gets 60% of the Jaguars' carries." **Wrong.** Coen, Aug 26 (Yahoo): "We're going to have to be a little bit more by committee." Camp settled into a three-back rotation — Tuten early downs, Chris Rodriguez Jr. inside and at the goal line, LeQuint Allen on third downs. *For:* majority of first-team reps, 4.28 speed, five rushing touchdowns on 83 rookie carries. *Risk:* sent home sick Sept 2; a 3.7-YPC back sharing goal-line work with a Coen favourite is a 150-point outcome. *Vegas:* Jaguars 8.5, over −140. *Price:* 78% at 53, 0% at 77. **Verdict: PASS**, and the corrected engine makes it clearer: at 53 he is 8.0 behind the best choice and **outside** the band that holds six other names, so he is not "level with Pitts" any more — he is worse there. **Jaylen Warren, identical 176 projection, is 90% available 24 picks later.**

**Luther Burden III (WR, CHI) — proj 168, +12.**
*Premise:* "3rd in YPRR last year behind Puka and JSN." **True on CBS's measure (2.71, 3rd of 152), not PFF's (2.34, tied 7th)** — and on **307 routes**, fewest in the top ten. *For:* target share 7.4% weeks 1–10 rising to 18.4% weeks 11–17 (Bleacher Nation, Aug 10); DJ Moore is in Buffalo; Ben Johnson is "buying Burden stock." *Risk:* Odunze is healthy, Loveland led the team in targets per route, and Burden's second-half pace extrapolates to 105 targets — a WR3, exactly his 168. *Vegas:* Bears 9.5, under −125. *ESPN price:* 58 against a mock 56, no discount. *Price:* 89% at 53, 0% at 77. **Verdict: PASS.** 16 behind the best choice at 53 and 22.5 behind at 44 — the worst gap of anyone on your list at any of your picks.

**Emeka Egbuka (WR, TB) — proj 192 (cut from 206), +36.**
*Premise:* "Evans left Tampa." **True** — three years with the 49ers, March 9. *For:* 127 targets as a rookie (63 / 938 / 6), 29.4% first-read target share, 2.49 YPRR before Mayfield's injury; Godwin is 30 and managed 360 yards. *Risk:* sprained toe Aug 12, no preseason snaps, out of team drills as of Sept 2 — Bowles: "I don't know how fast." I priced about a game and a half. *Vegas:* Bucs 8.5, under −135. *Price:* 89% at 29, 79% at 44, 23% at 53. **Verdict: PASS AT 29 AND 44 · LEVEL AT 53 IF HE IS THERE.** Milder than the v1 call and more honest: 19 behind Flowers at 29 and 12 behind Daniels at 44, both decisive — but at 53 he is one of the six inside the noise band, on 46 samples with a standard error of 2.5. Never a *plan*, because he is there fewer than one time in four.

**Jaylen Waddle (WR, DEN) — proj 174, +18.**
*Premise:* "Denver threw the most in the league." **True:** Bo Nix threw 612 passes, most in the NFL, at 6.4 yards per attempt — 28th of 33. Right about volume, silent about efficiency. *For:* Denver paid a first, a third and a fourth; Payton says he will "play everywhere except offensive line"; 64 / 910 / 6 as WR24 with bad quarterback play; a 899.5 receiving-yards prop consistent with my 174. *Risk:* Sutton is still the red-zone target, and a 14-3 team that just added a receiver throws 560 times, not 612. *Price:* 78% at 44, 28% at 53, 0% at 77. **Verdict: PASS.** 22 behind at 44 and 13 behind at 53 — closer than before, still outside the band — and ESPN prices him at 46 against a mock 46, so there is no market edge either.

**Kyle Pitts Sr. (TE, ATL) — proj 150, +34.**
*Premise:* "finished TE2." **True and hollow.** TE2 by total (166.8 points, 88 / 928 / 5), TE6 per game, 86 points behind McBride, three of five touchdowns in one game. *For:* Stefanski's Cleveland tight ends were second in the NFL in targets 2020–25; a three-year, $54M extension; consensus around 111 targets. *Risk:* Atlanta has still not named a quarterback — Penix (ACL) against Tua, "eventually" per NFL Network (Sept 2). Win total 6.5, over −140. *Price:* 85% at 53, 18% at 77. **Verdict: TAKE AT 53.** The biggest promotion on your list: the plan's pick at 53 (1,847), level with Tyler Warren and four other names, and the reason the tight end can wait past pick 20 at all — which is why London is the pick at 20 rather than Bowers. He wins his tie on availability and the empty slot, not on points.

**Colston Loveland (TE, CHI) — proj 159, +43.**
*Premise:* "Ben Johnson loves tight ends." **Half right.** LaPorta's 86-catch rookie year came under Johnson, but the better evidence is 2025: Loveland 82 targets / 58 / 713 / 6 in 16 games (TE12) with a team-high 29.1% target rate per route while Kmet fell to 48. *Risk:* Odunze, Burden and Swift all need the ball; 159 is a TE3 projection with no cushion. *ESPN price:* 41 against a mock 59 — an 18-pick move up. *Price:* 82% at 29, 15% at 44. **Verdict: PASS.** 23 behind Flowers at 29; at 44 he shows −6 on 38 samples with a standard error of 3.9 and 15% availability, the noisiest cell on the board. If you want a tight end early the honest options are Bowers or McBride at 20, or Pitts at 53.

**Three names to add.** **Alec Pierce** (WR, IND; ESPN 85 against a mock 63): level with the best at pick 92 and there 55% of the time — the plan's WR4, chosen over Brian Thomas Jr. and DK Metcalf on availability alone. **Chuba Hubbard** (RB, CAR): level with the best at 101 and there 93%, which in a pick where eight names are level is the entire argument. **Breece Hall** (RB, NYJ): the best single pick value at 44 (1,858), there 34% — the one back worth breaking the plan for.

**Reach rules applied to your actual picks.** A reach is earned by role certainty in a tier about to run out, capped at one round, and never justified for a player above about 80% at your next pick. Exactly one candidate passes: a tight end at 20, because both tier-1 tight ends are under 20% by pick 29. Everything else fails — Flowers 85% at 29, Daniels 81% at 44, Pitts 85% at 53, Warren 90% at 77, Hubbard 93% at 101. And do not reach for a back before 77 on scarcity grounds; with Brown kept, this board has no running-back scarcity to buy.

## 7. Sample drafts and the target build

Across the simulated drafts that follow the plan below, the projected starting lineup runs **1,763 to 1,877, mean 1,839** (sd 19.2). The ten sample drafts land between 1,814 and 1,867 — **53 points between best and worst, about three a week.** The structure matters far more than any individual name in it.

**Most-owned across those runs:** Jaylen Warren 87%, Zay Flowers 85%, Drake London 61%, Jayden Daniels 58%, Kyle Pitts Sr. 57%, Jaxon Smith-Njigba 52%, Brian Thomas Jr. 46%, Breece Hall 38%, Josh Jacobs 33%, Alec Pierce 32%.

**What happened in the ten samples:** a receiver at pick 5 in eight (Bijan in the other two); Flowers in nine, at pick 29 in all nine; a quarterback at 44 in seven, and in the other three the quarterback slid to 116 (Mahomes, Dart, Murray) because a back went at 44 instead; Pitts at 53 in eight (Josh Jacobs in the other two); Jaylen Warren at 77 in eight; the tight end filled at 20 in four and at 53 in six, with no pattern in the totals by which; kicker and defense in the last two rounds in all ten.

**The target build** (`plan_path`). `Control` is the arm where nothing is forced at that pick; `vs.` is what taking this player adds over just drafting sensibly there.

| Pick | Target | Pos | Projected lineup | Control | vs. | There | If he's gone | If he falls |
|---|---|---|---|---|---|---|---|---|
| KEEP | Chase Brown | RB | — | — | — | — | — | — |
| 5 | Jaxon Smith-Njigba | WR | 1,858 | 1,863 | −5.2 | 63% | Ja'Marr Chase (−5.6, 31%) | Bijan Robinson (21%) |
| 20 | Drake London | WR | 1,861 | 1,861 | +0.4 | 62% | Brock Bowers (level, 50%) | — |
| 29 | Zay Flowers | WR | 1,858 | 1,861 | −2.7 | 85% | Trey McBride (−3.8, 20%) | — |
| 44 | Jayden Daniels | QB | 1,852 | 1,858 | −5.9 | 81% | Bucky Irving (−3.7, 73%) | Breece Hall (34%) |
| 53 | Kyle Pitts Sr. | TE | 1,847 | 1,856 | −8.6 | 85% | Tyler Warren (level, 70%) | Josh Jacobs (27%) |
| 77 | Jaylen Warren | RB | 1,843 | 1,846 | −3.6 | 90% | Rhamondre Stevenson (−3.7, 49%) | — |
| 92 | Alec Pierce | WR | 1,842 | 1,842 | −0.5 | 55% | Brian Thomas Jr. (level, 48%) | — |
| 101 | Chuba Hubbard | RB | 1,839 | 1,842 | −2.9 | 93% | J. Croskey-Merritt (level, 70%) | RJ Harvey (17%) |
| 116 | Travis Kelce | TE | past horizon | — | — | 49% | Isaiah Likely (79%); Mark Andrews (55%) | — |
| 125 | Michael Pittman Jr. | WR | past horizon | — | — | 76% | Jayden Reed (98%); Isaiah Likely (62%) | — |
| 140 | Brandon Aubrey | K | past horizon | — | — | 56% | Cameron Dicker (68%), then a kicker at 164 | — |
| 149 | Woody Marks | RB | past horizon | — | — | 66% | Zach Charbonnet (53%); Mike Washington Jr. (56%) | — |
| 164 | Jordyn Tyson | WR | past horizon | — | — | 99% | Travis Hunter (100%) | — |
| 173 | Baltimore Defense | DEF | past horizon | — | — | 79% | Buffalo Defense (98%) | — |

`plan_check`: **pass** — every starting slot filled above replacement, no player named twice, one quarterback only, and the largest gap to any runner-up along the path is 5.6 points (pick 5).

**Read the vs. column, not the lineup column.** Seven of the eight rows are *negative*: the plan's target is worth slightly less than the control arm at that pick. That is the bias in §2, and it is why the plan totals 1,839 while the same drafter choosing freely totals 1,863. **The plan is a ranking, not a promise, and on this engine it does not beat drafting sensibly.** What it gives you is the order in which to take the top row still on the board — worth having on your knee at pick 92, when four names are level. If every target lands the nine starters sum to **1,871** (Daniels 347 · Brown 230 · Jaylen Warren 176 · Smith-Njigba 268 · London 227 · Pitts 150 · Flowers 215 at flex · Aubrey 155 · Baltimore 103); the rollouts say 1,839, the difference being the drafts where a target was gone plus that bias.

**Why this build.** Take the tier that is about to end (5, 29), the best player rather than a tier the lineup cannot distinguish (20), the quarterback before the wall between 53 and 77 (44), the tight end at the last window that exists (53), the second back at the last turn one exists (77), and the most available name in a tie (92, 101).

**The honest weakness: RB2.** Jaylen Warren is a timeshare and everything behind him is 27 or more points below replacement — one Chase Brown injury and you are starting Chuba Hubbard. **The hedge:** Breece Hall at 44 when he falls (34%), which pushes the quarterback to 53 (Daniels 57%, Hurts 64%) and the tight end to Pitts or Tucker Kraft at 77 (18% and 17%) with Kelce at 116 as the floor — expensive, so treat it as an opportunistic swap, not a design. **The second weakness** is that this build starts a 150-point tight end, which makes Atlanta naming Tua a real event for you.

**The upside case, not the plan:** Bijan at 5 (21%), London or Bowers at 20, Flowers at 29, Hall at 44 (34%), Jacobs at 53 (27%) — the whole sequence lands under one draft in ten. Take it, in that order, if the board offers it.

## 8. The late-round plan (picks 116–173)

The rollouts stop at pick 101. From here the ranking is projection over replacement plus availability, and **nothing back here changes your starting lineup except the kicker.**

- **The kicker exception, with the number attached.** Brandon Aubrey projects 155 against a replacement kicker's 130 and is **56% available at pick 140**, 23% at 149, 2% at 164. He now appears in the pick-140 table as the top surplus row on the board (+25), ahead of Cameron Dicker (+13, 68%). Taking him is worth about 19 points over Chase McLaughlin at 164 and costs a round-12 bench ticket worth nothing to your lineup. Kicker-last is right in most leagues; here it is worth the exception. If he is gone at 140, take Dicker (68%) or Jake Bates (85%).
- **Handcuffs.** Samaje Perine is not in the player pool — claim him in Week 1 waivers; he is the one handcuff that matters. Rico Dowdle is 13% at 92 and gone by 101, so the Pittsburgh split cannot be insured with a pick: Henderson (64%) or Pollard (80%) at 77 is the insurance, taken *instead of* Warren.
- **Tight-end insurance.** With Pitts as the TE1: Travis Kelce 49% at 116, Isaiah Likely 79%, Mark Andrews 55%, Jake Ferguson 80%. Take one.
- **Bench backs.** Everything from 116 on is 27 or more points under replacement, so pick for path to volume: Kyle Monangai (31% at 116), Woody Marks (93% at 125, 66% at 149), Zach Charbonnet (88% at 125), Rachaad White (71% at 125).
- **Next-year keepers.** Waiver pickups cannot be kept here, so a round-13-plus hit is the only cheap keeper you can manufacture. **Jordyn Tyson is 99% available at 164 and 96% at 173**, and **Travis Hunter is 100% at every one of your picks** — the draft ends before ADP reaches him.
- **Defense.** The room starts on kickers and defenses in round 11, so Seattle, Denver and Houston are under 5% by 140. Baltimore is 86% at 164 and 79% at 173; Buffalo 99% and 98%. Take the defense last and stream from Week 1.

## 9. Assumptions worth checking before you commit

- **Keeper rule:** same round, Brown at round 6, waiver pickups not keepable. If any of the three is wrong, re-read §1 first.
- **Lineup:** 12 teams, one flex, no superflex. A superflex slot would roughly double Daniels' keeper value and make him the conversation instead of Brown.
- **Fifteen rounds including K/DEF:** anyone with an ADP past about 155 goes undrafted, which is why the round-14 lottery tickets are free.
- **ESPN pricing covers the top 100 only;** players 101 and deeper carry mock ADP, so availability past pick 100 is approximate.
- **The plan is not a promise.** On this engine it simulates 24 points *below* the same drafter choosing freely at every pick. Use the ordering and the gaps, not the total; §2 has the accounting.
- **The one assumption that could flip the board: the projections.** Measuring lineups took the old flip-assumption (the RB-versus-WR baseline) off the table. **Smith-Njigba 268** — a 240-point receiver makes pick 5 Bijan-or-nothing. **Daniels 347** — if the rushing floor regresses the quarterback slides to 53 and 44 becomes Breece Hall. **Pitts 150** — if Atlanta starts Tua and he is a 125-point tight end, the tight end had to come at 20 and this build is wrong by about 25 points.
- **Injury flags to re-check Saturday:** Flowers (lower body), Egbuka (toe), Nabers (ACL), Jeanty (ankle), Tuten (sick Sept 2), Nacua (psoas), Chase (leg), Hall (groin), Henderson (ankle).
- **Real leaguemates are less rational than simulated ones.** The two managers who take a quarterback by round 4 every year push the run earlier than ESPN ADP says, so Daniels at 81% at pick 44 is optimistic and Hurts at 82% is your realistic floor. The compensation: receivers fall further than the model predicts.

## Appendix

**Terms.** *Pick value* — the projected final starting lineup if you take this player here and draft sensibly afterwards, over 200 simulated completions; it ranks every table in §4. *Control / vs. control* — the same drafts with nobody forced in at that pick, and the difference the candidate makes on his own samples. *Now* — measured against the player the pick recommends: TAKE on him, a positive number on anyone worth more if he fell to you, a negative number on anyone worth less. *Here / Next* — availability at that pick and the following one. *Level (≈)* — inside two standard errors of the recommended player: the simulation cannot tell them apart and neither should you. *Replacement level* — the worst player at a position who still has to start for someone every week, by flex equilibrium. *Surplus / "vs. free"* — projection minus that number; explanation only. *Flex fill* — how those slots split, 4 RB / 11 WR / 0 TE here. *Cost of waiting* — value lost at a position by waiting one more turn; the baseline cancels between the terms. *Keeper inflation* — with keepers removed, the player available at pick p is worse than ADP p suggests. *YPRR / TPRR* — yards and targets per route run (unstable under about 250 routes).

**Scoring applied.** 0.1/rush yd, 0.1/rec yd, 0.5/rec, 6/rush or rec TD, 0.04/pass yd, 4/pass TD, −2/INT, −2/fumble lost, 2/two-point; no TE premium, no bonuses.

**Sources and dates.** ADP: Footballguys cross-platform table, ESPN column, fetched Sept 3, 2026 (the page prints no date); FantasyFootballCalculator half-PPR 12-team mocks Aug 28–Sep 2 for the spread and everyone past the top 100; RotoWire ADP (Sept 2) for injury flags. The ESPN API returns alphabetical order without the filter header, so the Footballguys column stood in as the ESPN price. Win totals: VegasInsider (BetMGM), Sept 2; props from Sharp Football (Aug 31) and Yahoo (Aug 24). News and usage all fetched Sept 3, items dated Mar 9–Sept 3: PFF, Bleacher Nation, Yahoo, SI, PFT, FantasyFootballCalculator, FantasyPros, Footballguys, NBC, Athlon, Bengals.com, CBS, DenverSports, RotoWire. ESPN.com and Pro Football Rumors did not load (JS/robots).

**Projections I changed from consensus (five), from my Sept 3 set:** Egbuka 206 → 192 (toe Aug 12, no team drills as of Sept 2); Tuten 200 → 176 (Coen's "more by committee", Aug 26; Rodriguez has the goal line); Bucky Irving 201 → 188 (Gainwell and Tucker have real roles; 3.4 YPC in 2025); Nabers 207 → 197 (ACL, would not commit to Week 1); Jeanty 199 → 191 (ankle Aug 23, side work only Sept 1).

**Simulation settings.** `draft_sim.py --sims 1500 --pick-values --keeper-scenarios --samples 10`, seed 1000.

- **Availability:** 1,500 drafts, twelve keepers drawn per run (weighted toward better players, rounds correlated to quality). Opponents draft ESPN ADP plus capped noise scaled to each player's spread, positional need from round 8, kickers and defenses on a rising curve from round 11 — which is why K and DEF appear in the availability tables from round 12 and Brandon Aubrey is a real option at 140. **Your own seat drafts off ADP like everyone else**: "will he still be there" has to be a fact about the room.
- **Pick values:** 200 rollouts per pick, up to 8 candidates plus your roster and your list, through round 9. Common random numbers; a matched no-forced-pick control arm on the same samples; a two-standard-error noise threshold; a 50% availability floor for a plan target; and no candidate measured on fewer than 25 drafts may anchor the **Now** column. `cost_of_waiting` is computed to the same depth the board renders, so it stops at 101.
- **Three scales, not interchangeable.** (1) **Pick values** compare only *within* a pick, against that pick's own control arm; the column drifts down because each control assumes you followed the plan to get there. (2) **The plan total, 1,839**, is a full draft forcing the plan's targets. (3) **Keeper-scenario totals** come from their own 1,000-draft free-running pass. Never subtract across the three.
- **The plan trails the free policy by 24 points, and that is a defect, not a footnote** (§2 has the argument). The free-running heuristic scores 1,863 as the control arm at pick 5 and 1,864 on the keeper pass — the same policy measured twice, agreeing to within a point — while the plan scores 1,839. Part is unavoidable, and the adaptive board recovers most of it. Part is not: the rest-of-draft policy inside a rollout is the same heuristic, so a forced pick leaves it repairing a roster shape it did not plan, and the candidate is charged for that rigidity as well as his own merits — a real bias against exactly the picks where the rollouts disagree most interestingly with the heuristic. **Top item for v2.1.** The rankings and within-pick gaps survive it; the totals do not.
- **Keeper surplus** (the table in §1) is measured against a 400-run keeper-free probe and is slightly conservative: the real alternative at pick 68 is a little worse once other teams' keepers are gone.
- **Measured net keeper inflation:** +11.2 picks at 5, +7.9 at 20, +6.1 at 29, +3.9 at 44, +2.9 at 53, +0.5 at 77, +0.1 at 92, 0.0 at 101.
- **Replacement:** flex equilibrium — QB12 312, RB28 164, WR35 156, TE13 116, K12 130, DEF12 101; flex fill 4 RB / 11 WR / 0 TE. Used for the tier boards' "vs. free" column, for the cost-of-waiting differences, and nothing else.
- ADP deltas quoted in §4 and §6 come from comparing `players.csv` against `players_mock-adp.csv`, not from a second simulation.

**Assumptions.** Lineup exactly as configured. Injuries baked into expected games rather than modelled separately. Kickers and defenses near-interchangeable, with the one priced exception in §8. Players not in `players.csv` — Samaje Perine, Sean Tucker — are waiver targets. The rollout horizon is round 9; every recommendation past pick 101 is made on surplus and availability, and is labelled as such.
