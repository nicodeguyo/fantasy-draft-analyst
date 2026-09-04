# How this example was produced

A worked run of the `fantasy-draft-analyst` skill on Thursday, September 3, 2026, for a 12-team ESPN half-PPR keeper league drafting Sunday, September 6 (`league.yaml`: pick 5, one same-round keeper, 4-pt pass TD, −2 INT, one flex). Regenerated September 4 on the **v2 rollout engine**: every pick is now ranked by the starting lineup it leaves you with rather than by surplus. Everything in this folder was generated from the files listed at the bottom; nothing was hand-edited after the scripts ran except the prose.

## Inputs

- **Projections** are the analyst's own, built Sept 3 from 2025 production and 2026 roles and scored in this league's settings (`players.csv`, 229 players). Five were changed after draft-week research, with the reason in each row's `note` column and in the analysis appendix:
  1. Emeka Egbuka 206 → 192 — sprained toe Aug 12, no team drills as of Sept 2 (Bowles: "I don't know how fast").
  2. Bhayshul Tuten 200 → 176 — Liam Coen, Aug 26: "more by committee"; Rodriguez has the goal line.
  3. Bucky Irving 201 → 188 — Gainwell used heavily on flat routes and in the pony package (OC Zac Robinson, Aug 5); Tucker trusted at the goal line (Aug 30); 3.4 YPC in 2025.
  4. Malik Nabers 207 → 197 — ACL/meniscus (Week 4, 2025); would not commit to Week 1 (Sept 1).
  5. Ashton Jeanty 199 → 191 — sprained ankle Aug 23, side work only Sept 1, not on IR.
  `players.csv` and `league.yaml` were **not** touched in the v2 regeneration — only the engine changed, so the difference between the v1.1 and v2.0 outputs is the method and nothing else.
- **ADP.** The pool arrived priced with FantasyFootballCalculator half-PPR 12-team mock ADP (Aug 28–Sep 2, 2026) and its standard deviation; that file is kept as `players_mock-adp.csv`. Because the league is on ESPN, the top 100 were repriced with the ESPN column of the Footballguys cross-platform ADP table (fetched Sept 3, 2026; the page prints no date), keeping the FFC spread — the step `scripts/merge_adp.py` performs. Players beyond the top 100 keep mock ADP.
- **Betting market.** VegasInsider win totals (BetMGM lines, Sept 2, 2026). Season props from Sharp Football Analysis (Aug 31) and Yahoo (Aug 24).
- **News and usage** (all fetched Sept 3, 2026): RotoWire news feed and ADP page; FantasyPros injury news and 2025 TE stats; FantasyFootballCalculator per-player news pages for Tuten, Waddle, Egbuka, Gibbs, Hampton, Brown, Flowers, Hall, Bowers and Irving (items dated Aug 5–Sept 2); PFF 2025 YPRR leaders (Jul 7); Bleacher Nation on Burden (Aug 10) and Bears TEs (Jul 24); Fantasy Footballers on Egbuka (Jul 10); Yahoo and SI on Coen's backfield plan (Aug 26, Jul 22); PFT on Rodriguez (Jun 9), Gibbs (Aug 6) and Jeanty (Sept 1); Athlon on Nabers (Sept 1) and Irving/Gainwell (Jul 7); Pewter Report (Aug 5); Bengals.com RB preview (Jun 25); Footballguys Pitts spotlight (Jul 29); Yahoo/Schefter on the Falcons QB (Sept 1); DenverSports on Nix (Aug 11). ESPN.com story pages and Pro Football Rumors could not be fetched; Yahoo/NBC mirrors were used.

## Simulation

```
python3 scripts/draft_sim.py --league league.yaml --players players.csv \
    --sims 1500 --samples 10 --pick-values --keeper-scenarios --out sim.json
```

About 5 minutes 40 seconds on a laptop; the board renders in under a second. Seed 1000; keeper Chase Brown at round 6 (pick 68 forfeited). Same seed reproduces `sim.json`, `sim_availability.csv` and the console summary byte for byte.

- **Pick values.** For each of the eight picks through round 9, up to 8 candidates were each planted at that pick and the rest of the draft simulated 200 times — the room drafting ESPN ADP plus capped noise, positional need from round 8, K/DEF on a rising curve; the simulated "you" drafting by the lineup-aware heuristic afterwards. Every candidate branches from the same prefix draft (common random numbers), and each sample is also played out with nobody forced in, so a candidate is scored on the *difference* he makes on his own samples rather than on the luck of the board he happened to land in.
- **The plan path** (`plan_path`) is greedy by pick value, pick by pick, with a 50% availability floor: a better player who falls to you less often than that is reported as the row's upside, not as the plan. Jaxon Smith-Njigba 5 · Drake London 20 · Zay Flowers 29 · Jayden Daniels 44 · Kyle Pitts Sr. 53 · Jaylen Warren 77 · Alec Pierce 92 · Chuba Hubbard 101. `plan_check`: pass.
- **The keeper verdict** is scenario-based (`--keeper-scenarios`): full drafts under each case, compared on mean final starting lineup. Brown 1,864 ±0.6 · Daniels 1,827 · Bowers 1,824 · McMillan 1,813 · nobody 1,810. The isolated surplus table stays in the analysis as the explanation.
- **Cost of waiting** (`cost_of_waiting`) replaces v1's position heatmap: points lost per position by waiting one more turn. It is invariant to the replacement level, which is the point — overriding `roster.replacement_rank` for RB by ±20 moves the RB cells by at most 4 points, where it moves the surplus levels they are built from by up to 73.
- **Availability.** 1,500 drafts with your own seat drafting off ADP, so "still there at your next pick" measures the room rather than your own plan. Net keeper inflation in force: +11.2 at pick 5, +7.9 at 20, +6.1 at 29, +3.9 at 44, +2.9 at 53, +0.5 at 77.
- **Replacement level** (flex equilibrium, RB28 = 164 · WR35 = 156 · TE13 = 116 · QB12 = 312, flex filling 4 RB / 11 WR / 0 TE) is still computed and still shown — in the appendix and as the tier boards' "vs. free" column. It no longer ranks anything.
- **One honest number.** Following the plan simulates to 1,839; letting the same simulated drafter choose freshly at every pick gives 1,863. `methodology.md` §2 explains why and names it as the first thing to fix in v2.1.
- Outputs: `sim.json`, `sim_availability.csv` (There % for every player at every one of your picks), `sim_summary.md` (console output).

## Board

```
python3 scripts/build_board.py --league league.yaml --sim sim.json \
    --notes notes.json --players players.csv --out draft-board.html
```

Default renderer settings (top 5 rows per pick through round 9, plus every pick that has a note), Seahawks theme from `league.yaml`. Pick tables are ranked by pick value with the "Now" column; the plan renders from `plan_path`; cost of waiting replaces the roadmap; replacement level sits in the appendix. Every v1.1 interaction still works (tap-to-cross-off, ✓ to draft, undo, hide-taken, the lineup strip, NOW nav, saved state, print) — checked with Playwright after the rewrite.

## Files

`league.yaml` · `players.csv` (ESPN-priced, five projections adjusted) · `players_mock-adp.csv` (as delivered) · `sim.json` · `sim_availability.csv` · `sim_summary.md` · `notes.json` · `draft-board.html` · `analysis.md` · `RUNLOG.md`
