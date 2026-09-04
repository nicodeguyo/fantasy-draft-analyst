# How this example was produced

A worked run of the `fantasy-draft-analyst` skill on Thursday, September 3, 2026 (regenerated September 4 on the flex-equilibrium replacement model), for a 12-team ESPN half-PPR keeper league drafting Sunday, September 6 (`league.yaml`: pick 5, one same-round keeper, 4-pt pass TD, −2 INT, one flex). Everything in this folder was generated from the files listed at the bottom; nothing was hand-edited after the scripts ran except the prose.

## Inputs

- **Projections** are the analyst's own, built Sept 3 from 2025 production and 2026 roles and scored in this league's settings (`players.csv`, 229 players). Five were changed after draft-week research, with the reason in each row's `note` column and in the analysis appendix:
  1. Emeka Egbuka 206 → 192 — sprained toe Aug 12, no team drills as of Sept 2 (Bowles: "I don't know how fast").
  2. Bhayshul Tuten 200 → 176 — Liam Coen, Aug 26: "more by committee"; Rodriguez has the goal line.
  3. Bucky Irving 201 → 188 — Gainwell used heavily on flat routes and in the pony package (OC Zac Robinson, Aug 5); Tucker trusted at the goal line (Aug 30); 3.4 YPC in 2025.
  4. Malik Nabers 207 → 197 — ACL/meniscus (Week 4, 2025); would not commit to Week 1 (Sept 1).
  5. Ashton Jeanty 199 → 191 — sprained ankle Aug 23, side work only Sept 1, not on IR.
- **ADP.** The pool arrived priced with FantasyFootballCalculator half-PPR 12-team mock ADP (Aug 28–Sep 2, 2026) and its standard deviation; that file is kept as `players_mock-adp.csv`. Because the league is on ESPN, the top 100 were repriced with the ESPN column of the Footballguys cross-platform ADP table (fetched Sept 3, 2026; the page prints no date), keeping the FFC spread — the step `scripts/merge_adp.py` now performs. Players beyond the top 100 keep mock ADP.
- **Betting market.** VegasInsider win totals (BetMGM lines, Sept 2, 2026). Season props from Sharp Football Analysis (Aug 31: Chase Brown 824.5 rushing yards / 5.5 rushing TDs; Montgomery 825.5 / 7.5) and Yahoo (Aug 24: Waddle 899.5 receiving yards, Walker 950.5 rushing yards, McBride u100.5 receptions, Kyren u9.5 rushing TDs, Achane u1,000 rushing yards, Caleb Williams o3,645 passing yards).
- **News and usage** (all fetched Sept 3, 2026): RotoWire news feed (Sept 3) and ADP page (Sept 2); FantasyPros injury news and 2025 TE stats; FantasyFootballCalculator per-player news pages for Tuten, Waddle, Egbuka, Gibbs, Hampton, Brown, Flowers, Hall, Bowers, Irving (items dated Aug 5–Sept 2); PFF 2025 YPRR leaders (Jul 7); Bleacher Nation on Burden (Aug 10) and Bears TEs (Jul 24); Fantasy Footballers on Egbuka (Jul 10); Yahoo and SI on Coen's backfield plan (Aug 26, Jul 22); PFT on Rodriguez's foot surgery (Jun 9), Gibbs (Aug 6) and Jeanty (Sept 1); Roundtable (Jul 30); Athlon on Nabers (Sept 1) and Irving/Gainwell (Jul 7); Pewter Report (Aug 5); Bengals.com RB preview (Jun 25); Buccaneers.com (Feb 6); Footballguys Pitts spotlight (Jul 29); Yahoo/Schefter on the Falcons QB (Sept 1); NBC/Wolfe (Sept 2); DenverSports on Nix's 612 attempts (Aug 11); CBS on Evans to the 49ers (Mar 9). ESPN.com story pages and Pro Football Rumors could not be fetched; Yahoo/NBC mirrors were used.

## Simulation

`python3 scripts/draft_sim.py --league league.yaml --players players.csv --sims 1500 --samples 10 --out sim.json`

- 1,500 drafts, seed 1000; keeper Chase Brown at round 6 (pick 68 forfeited). Twelve league keepers drawn per run, weighted toward better players with keeper rounds correlated to quality (the league had not published its list). Opponents draft ESPN ADP plus noise scaled to each player's spread (capped), positional need from round 8, kickers and defenses on a rising curve from round 11; the simulated "me" weighs the opportunity cost of waiting at each position and keeps its bench balanced.
- Replacement level by **flex equilibrium**: dedicated slots first, then the 12 flex slots and 3 bye/injury slots go to the best remaining RB/WR/TE regardless of position. That fills the flex 4 RB / 11 WR / 0 TE and prices RB28 = 164, WR35 = 156, TE13 = 116, QB12 = 312 (`replacement`, `flex_fill` in `sim.json`). An earlier fixed 55/40 flex split priced RB34 = 137 and made the model hoard running backs; the keeper surplus for Brown moved from +54 to +35 and the target build from four backs to a two-receiver lineup with a receiver at flex.
- The **position plan** (`position_plan`): expected best surplus still available at each position at each of the user's picks — rendered as the roadmap heatmap on the board and read in §3 of the analysis (receiver holds value through 92, tight end windows at 20 and 53, running back positive only through 77, quarterback flat until 53).
- Net keeper inflation measured in-sim (extra players gone beyond the pick number): +11.2 at pick 5, +7.9 at 20, +6.1 at 29, +3.9 at 44, +2.9 at 53, +0.5 at 77, +0.1 at 92.
- Outputs: `sim.json` (keeper table, replacement and flex fill, position plan, availability, sample drafts, most-owned, inflation), `sim_availability.csv` (There % for every player at every one of the user's picks), `sim_summary.md` (console output).
- The mock-ADP comparison figures quoted in the analysis come from the same command run on `players_mock-adp.csv`; that output is not shipped.
- Run time: about 45–55 seconds per 1,500-run simulation on a small container; the board renders in under a second.

## Board

`python3 scripts/build_board.py --league league.yaml --sim sim.json --notes notes.json --players players.csv --out draft-board.html`

Default renderer settings (top 7 per pick through round 9, plus every pick that has a note). Seahawks theme from `league.yaml`. `notes.json` follows the current schema: a `plan` with a Plan B (`alt`) for every pick, `roadmap_note` for the position-plan heatmap, and `pick_notes` as `{note, plan_b}`. Every player named in a pick note or Plan B appears in that pick's table; the plan's starting lineup fills 2 WR plus a receiver at flex, and the lineup tracker and roadmap render from `sim.json`.

## Files

`league.yaml` · `players.csv` (ESPN-priced, five projections adjusted) · `players_mock-adp.csv` (as delivered) · `sim.json` · `sim_availability.csv` · `sim_summary.md` · `notes.json` · `draft-board.html` · `analysis.md` · `RUNLOG.md`
