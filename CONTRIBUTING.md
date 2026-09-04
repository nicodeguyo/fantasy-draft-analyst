# Contributing

The most valuable contributions, in order:

1. **Verified data sources.** A URL that loads without a login, what it returns, and the date stamp it prints. Add it to `skills/fantasy-draft-analyst/references/data-sources.md` with the same columns as the existing table. Sources that only work from a shell (headers, JS) go in a separate line so chat-only users don't chase them.
2. **Platform ADP quirks with evidence.** "Yahoo rooms take X early" needs a link to the data or the article that shows it, and the season it was observed.
3. **Keeper-rule variants** the taxonomy in `references/keeper-rules.md` doesn't cover, with how the math changes.
4. **Simulator improvements** in `scripts/draft_sim.py` — better opponent models, a better rest-of-draft policy inside the rollouts (the weakest link: a mediocre policy shrinks the differences between candidates), auction support, published-keeper handling. Keep it standard-library plus PyYAML, keep the `sim.json` schema backward-compatible, and run the sample league before and after (`examples/sample-league/`) so the change is visible.
5. **Example runs** for other league shapes (superflex, 10-team PPR, TE-premium) in `examples/<name>/` with the same files as the sample league and a `RUNLOG.md` that says where every number came from.

Style: the reference files explain *why*, not just what. Prefer a sentence of reasoning to a MUST. Keep `SKILL.md` under ~150 lines; detail belongs in `references/`.

Re-package the skill after changing anything under `skills/fantasy-draft-analyst/`:

```bash
./scripts/package.sh   # rebuilds dist/fantasy-draft-analyst.zip
```

Please don't submit anything that requires paid data or a login to run — the whole point is that it's usable by anyone.

## Season rollover

The season is a setting, not a constant: `league.yaml` has `season`, `fetch_adp.py` takes `--season`, and the URLs in `references/data-sources.md` embed the year. Each August, bump the defaults, re-verify every source in the data-sources table (sites move), re-run the sample league, and bump `metadata.version` in `SKILL.md`.
