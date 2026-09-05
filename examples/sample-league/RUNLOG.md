# Sample League: source record and reproduction

This is a fictional 12-team ESPN half-PPR league, pick 5, with one same-round keeper per team. The saved player inputs were assembled September 3, 2026; later launch revisions corrected keeper ownership, aligned the board and benchmark policy, and clarified statistical interpretation. Rebuilding the model does not refresh player data.

The source descriptions below are the original analyst’s provenance record. Projections are analyst/model-authored, not an official ESPN feed or independently validated consensus. This launch review did not independently reverify every dated player-news claim or source term. Use these files to reproduce an example; fetch fresh, dated public inputs for a real league.

## Inputs

- **Projections** are the analyst's own, built Sept 3 from 2025 production and 2026 roles and scored in this league's settings (`players.csv`, 229 players). Five were changed after draft-week research, with the reason in each row's `note` column and in the analysis appendix:
  1. Emeka Egbuka 206 → 192 — sprained toe Aug 12, no team drills as of Sept 2 (Bowles: "I don't know how fast").
  2. Bhayshul Tuten 200 → 176 — Liam Coen, Aug 26: "more by committee"; Rodriguez has the goal line.
  3. Bucky Irving 201 → 188 — Gainwell used heavily on flat routes and in the pony package (OC Zac Robinson, Aug 5); Tucker trusted at the goal line (Aug 30); 3.4 YPC in 2025.
  4. Malik Nabers 207 → 197 — ACL/meniscus (Week 4, 2025); would not commit to Week 1 (Sept 1).
  5. Ashton Jeanty 199 → 191 — sprained ankle Aug 23, side work only Sept 1, not on IR.
  These are saved input changes from the original example. The source record does not independently validate those assumptions.
- **ADP.** The pool arrived priced with FantasyFootballCalculator half-PPR 12-team mock ADP (Aug 28–Sep 2, 2026) and its standard deviation; that file is kept as `players_mock-adp.csv`. Because the league is on ESPN, the top 100 were repriced with the ESPN column of the Footballguys cross-platform ADP table (fetched Sept 3, 2026; the page prints no date), keeping the FFC spread — the step `scripts/merge_adp.py` performs. Players beyond the top 100 keep mock ADP.
- **Betting market.** VegasInsider win totals (BetMGM lines, Sept 2, 2026). Season props from Sharp Football Analysis (Aug 31) and Yahoo (Aug 24).
- **News and usage** (all fetched Sept 3, 2026): RotoWire news feed and ADP page; FantasyPros injury news and 2025 TE stats; FantasyFootballCalculator per-player news pages for Tuten, Waddle, Egbuka, Gibbs, Hampton, Brown, Flowers, Hall, Bowers and Irving (items dated Aug 5–Sept 2); PFF 2025 YPRR leaders (Jul 7); Bleacher Nation on Burden (Aug 10) and Bears TEs (Jul 24); Fantasy Footballers on Egbuka (Jul 10); Yahoo and SI on Coen's backfield plan (Aug 26, Jul 22); PFT on Rodriguez (Jun 9), Gibbs (Aug 6) and Jeanty (Sept 1); Athlon on Nabers (Sept 1) and Irving/Gainwell (Jul 7); Pewter Report (Aug 5); Bengals.com RB preview (Jun 25); Footballguys Pitts spotlight (Jul 29); Yahoo/Schefter on the Falcons QB (Sept 1); DenverSports on Nix (Aug 11). ESPN.com story pages and Pro Football Rumors could not be fetched; Yahoo/NBC mirrors were used.

## Reproduce the current sample

From the repository root with Python and PyYAML installed:

```bash
python skills/fantasy-draft-analyst/scripts/draft_sim.py \
  --league examples/sample-league/league.yaml \
  --players examples/sample-league/players.csv \
  --sims 1500 --samples 10 --pick-values --keeper-scenarios \
  --out output/sim.json
python skills/fantasy-draft-analyst/scripts/build_board.py \
  --league examples/sample-league/league.yaml \
  --sim output/sim.json --notes examples/sample-league/notes.json \
  --players examples/sample-league/players.csv --out output/draft-board.html
```

Create `output/` first. Default seed is 1000. Keeper scenarios run before the board: up to four eligible surplus-shortlisted candidates plus keeping nobody, with the highest simulated mean selected unless explicitly overridden. Opponent keepers occupy their owners’ rosters and consume the correct round.

Candidate estimates use matched controls on states where each candidate is available. Reported uncertainty is Monte Carlo noise under fixed inputs. The control adjustment does not guarantee equivalent candidate populations or unbiased rankings. Availability is unconditional pre-draft frequency, not live pass-up survival.

The score sums season projections for one best legal starting lineup. Weekly lineup changes, injuries after drafting, waivers, and bench insurance are not evaluated. Historical totals and policy improvements from before the launch corrections are superseded; read the current generated simulation and benchmark outputs for current evidence.

## Board and policy evidence

The renderer and benchmark share the displayed candidate policy. Follow the prepared target and alternatives, including expanded rows, with configured exclusions, position caps, and enough remaining picks reserved for unfilled starting slots. Late targets from `notes.json` are part of that policy; when listed candidates run out, the shared surplus fallback applies.

The separate adaptive policy reacts to the simulated roster using its heuristic. The ADP-based bot is a baseline, not a verified platform autopick replica. Shared seeds couple randomness, but subsequent rooms can diverge. Benchmark differences are internal projected-lineup differences, not real-season gains.

The board’s tracking controls update local marks and the visible lineup; they do not rerun the simulation. The board, demo, screenshots, and benchmark should all be regenerated from the same saved inputs before a release.

## Files

- `league.yaml`: fictional rules and draft slot.
- `players.csv`: saved ESPN-priced player inputs and analyst projections.
- `players_mock-adp.csv`: original mock-market inputs.
- `sim.json` and `sim_availability.csv`: generated model results.
- `notes.json`: explanatory text, tier groups, and explicit late targets.
- `draft-board.html`: generated interactive board.
- `analysis.md`: how to read the current example.
