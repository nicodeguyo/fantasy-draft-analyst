# Archived v2 benchmark

This is historical evidence about the saved v2 preparation policy. It does **not** evaluate v3, compare competing assistants, or establish better real-season results.

<!-- benchmark:start -->
Archived v2 benchmark (does not evaluate v3): across 800 simulated drafts, the saved-board policy produced 90 more projected starting-lineup points than the noisy ADP-based draft bot, on average.

| Drafting policy | Mean projected lineup total |
|---|---:|
| Noisy ADP-based draft bot | 1,761 |
| Saved-board policy | 1,851 |
| Adaptive heuristic | 1,864 |

**Internal simulation, not real-season results.** The metric is the sum of projections for one best legal starting lineup. The paired difference is +90.1 ± 3.5 points (approximately 95% Monte Carlo interval). This interval excludes projection and model uncertainty. Weekly substitutions, injury coverage and bench value are not scored. The baseline is our noisy ADP-based draft bot, not verified platform autopick.

The benchmark follows the same saved player order and documented fallback as the displayed board. It does not model every choice a human user might make. [Exact results and input hashes](../../examples/sample-league/benchmark.json).
<!-- benchmark:end -->

## Reproduce the historical comparison

With Python 3.10+ and PyYAML, from the repository root:

```bash
python scripts/compare_policies.py --league examples/sample-league/league.yaml --players examples/sample-league/players.csv --sim examples/sample-league/sim.json --drafts 800
```

This command uses the legacy policy. New draft runs use `roster_v2`, whose objective includes modeled roster coverage, and will differ from saved v2 results. Keep this historical comparison separate from claims about the current release.

[Archived website and worked example](v2-site.html) · [Saved v2 inputs](../../examples/sample-league/) · [Current v3 example](../site/README.md)

The old screenshot, GIF, narrated video, and captions remain in `docs/media/` for historical reference. They describe preparation-only tracking and an old objective; they are not the current product demonstration.
