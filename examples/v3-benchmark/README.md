# V3 draft benchmark and recommended marketing claims

Run: September 7, 2026. Results behind the published v3 benchmark.

## Main result

**V3 averaged 66.2 more projected starting-lineup points than disciplined ADP drafting across 800 simulated draft rooms.**

| Policy | Projected starting-lineup points | Difference versus disciplined ADP |
|---|---:|---:|
| Disciplined ADP | 1,813.2 | — |
| Noisy ADP bot | 1,775.1 | −38.1 |
| Legacy heuristic on the same data | 1,880.9 | +67.7 |
| V3 live policy | 1,879.4 | +66.2 |

V3 was ahead of disciplined ADP in 793/800 rooms (99.1% of these simulated comparisons), with a positive average difference at every draft position. All four policies completed legal starting lineups in every room.

V3 versus noisy ADP: +104.3 points. This is a current comparison with that style of baseline, not a rerun of the exact historical +90 saved-board experiment.

V3 versus the legacy heuristic: −1.5 starter points, +0.49 bench-coverage utility, and −0.98 total roster utility. The legacy comparator uses the same current projections; it is not the old published preparation board. Do not claim that v3 beats v2 on starter points based on this run.

## Additional measures

| Measure | Disciplined ADP | V3 | Interpretation |
|---|---:|---:|---|
| Bench-coverage utility | 3.05 | 4.59 | +1.54 under the engine's stated absence assumptions; separate from projected starter points |
| Bench improvement over waiver-only fallback during one RB/WR/TE starter's absence | 0.221 | 0.369 | +0.148 projected points in an average one-week scenario; too small for a percentage-based marketing headline |
| Weekly lineup after one RB/WR/TE starter is removed, including bench and waiver replacements | 104.65 | 107.40 | V3 retains a +2.75 projected-point edge in this controlled stress test |

The absence calculation uses projected season points /17 for every player, the same fixed waiver replacement rates, and averages over RB/WR/TE starter removals. It does not simulate injury probabilities, timing, correlated absences, or actual weekly results. A stronger lineup can lose more points when a star is removed; the test does not establish a lower probability of injuries or fantasy losses.

## More useful Walker/Rice explanation

Expanded the public example from 8 to 800 conditional next-turn scenarios using the shipped comparison function.

- Take Rice at 20: Walker remained at 29 in 11/800 scenarios (1.4%).
- Take Walker at 20: Rice remained at 29 in 247/800 scenarios (30.9%).
- The Walker-first path led the Rice-first path by 7.457 utility points over the next two selections. At this early roster state the compared choices fill starting slots; this is a two-pick scenario result, not a full-draft advantage.
- After Walker, next selections were Williams 310 times, Rice 247, Olave 231, Hall 11, and McBride once.

Suggested card copy:

**Why take Walker now?** He rarely made it to your next pick in the simulations. Taking him now preserves more options at pick 29—including Rice and Olave.

Expandable evidence can show the counts and two-pick comparison, replacing the obvious 'lower projection changes the leader' marketing line.

## Proposed copy and visual hierarchy

Hero proof: **+66 projected starting-lineup points.**

Support: **Our v3 draft policy averaged 66 more points than disciplined ADP drafting across 800 simulated drafts.**

Chart: **ADP drafting: 1,813 → V3: 1,879.**

Secondary proof: **Stronger projected lineup in 793 of 800 simulated drafts.** Do not label this a win rate.

Example card: **Take Walker now. Keep your options open at 29.** Show availability counts in the drill-down.

Bench protection: retain a supporting explanation; do not turn the small absolute bench gain into an inflated percentage headline. Starter surplus overlaps with starting-lineup value and must not be added again. No championship-odds or reduced-injury-risk claim is supported.

One adjacent method note is sufficient for the marketing page: *Internal simulation · 800 draft rooms · 12-team half-PPR · all 12 draft positions · saved September 7 projections.* Link to the full method and data. The full report should explicitly name the tested live policy and baseline rules.

## Method and reproducibility

- 800 rooms, each run with all four policies: 3,200 completed simulated drafts.
- 12 teams, 15 rounds, half-PPR, no keepers, QB/2RB/2WR/TE/FLEX/K/DEF plus six bench spots.
- Seats cycle 1–12; seats 1–8 receive 67 rooms and seats 9–12 receive 66.
- Same frozen ESPN/CBS/FantasyPros-derived player pool for every policy. Limited data coverage; source dates and assumptions preserved in the evidence sidecar.
- Same per-pick opponent random seeds. Different choices change the remaining pool and subsequent draft paths.
- Disciplined ADP respects roster caps and legal completion, waits until the final two rounds for K/DEF, and avoids redundant QB/TE picks.
- V3 uses the exact live policy ordering without pre-draft horizon probes. All 15 decisions in a verification draft were checked against the shipped `live_draft.recommend()` function.
- No policy tuning or selection of favorable draft slots after seeing results. The 12-room execution pilot is included within the 800-room count.
- Forecasts both guide drafting and score the final projected lineup. This evaluates roster construction under those forecasts; it does not evaluate forecast accuracy or realized season outcomes.
- Paired Monte Carlo interval for the +66.226-point difference: approximately +64.0 to +68.5. This captures draft sampling variation, not source/model uncertainty.

Full room-by-room results are in [results-800.json](results-800.json), next-turn results in [next-turn-800.json](next-turn-800.json), and source hashes in [manifest.json](manifest.json). The complete research table includes the legacy comparator; the marketing table focuses on v3 versus ADP drafting.

Reproduce all 800 rooms from the repository root with Python 3.10+ and PyYAML:

```bash
python scripts/benchmark_v3.py 800
```

The prepared CSV is derived from the [public frozen snapshot](../v3-live/evidence.json), using the [example league](../v3-live/league.json) and `prepare_data.py --as-of 2026-09-07T04:00:17.778842+00:00`. The benchmark uses the shipped live policy order and no horizon probes. Source/model uncertainty is separate from the reported draft-sampling interval.
