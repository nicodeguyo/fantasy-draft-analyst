# Evidence preparation and shared toolkit core

Read this when collecting, importing or refreshing data. `prepare_data.py --help` is the command contract; `fantasy_core.evidence.prepare_snapshot` implements validation and aggregation. Keep user data outside the installed skill and public repository.

## Snapshot contract

The versioned snapshot distinguishes season, period (`season`, `week`, `rest_of_season`) and optional week. Each player has a stable `player_id`, display name, position, team, provider IDs and aliases. Team is metadata, not identity. Projection records retain original source, independence group, source URL, fetched/updated dates and statistical fields. ADP records retain source, season, format, value and date. News records retain the event, original evidence and timing.

Inspect the bundled synthetic evidence example and the CLI help for the exact executable schema. Synthetic fixtures demonstrate shape and failure handling; they are not current NFL data. Provider adapters are individually testable and source failures must appear in the report.

## Required data checks

- Match identities explicitly. Reject duplicate IDs and ambiguous aliases; retain unresolved import rows for correction.
- Align source season and period before combining forecasts. A 17-game season total cannot be mixed with a weekly forecast.
- Re-score each eligible source in the actual league rules. Average within known independence groups before combining groups so duplication does not increase influence.
- Preserve per-source scores and between-source dispersion. This dispersion measures disagreement, not the player's full performance distribution.
- Distinguish structural zero, observed/projected zero, missing and malformed values. Required position-specific stats must be complete; optional unavailable fields remain documented.
- Check price separately. Missing ADP does not justify inventing pick 999 or substituting expert rank. Unpriced players can remain research candidates but do not automatically qualify for an ADP-driven rollout.
- A timestamp for fetching a page is not the date of its underlying projection. Re-fetching an old page does not refresh its evidence.

The full evidence report accompanies the compact CSV. Legacy CSV imports cannot recover provenance that was never recorded; mark those inputs unverified/limited. When only rankings are usable, report tiers and roster structure without point-valued recommendations.

## News and changes

Normalize injury, recovery, suspension, release and role events, then deduplicate by their underlying event/source. Retain superseded events for review. Later publication alone does not defeat better-quality contradictory evidence. Keep unresolved conflicts visible.

Store analyst adjustments separately with before/after assumptions and reasons. Confirm whether a provider's current projection already reflects the event. An unavailable player might need both lower season production and reserve coverage, but must not receive the same missed-games discount twice.

Metrics should carry their source, denominator and period: routes per team dropback differ from targets per route; target share differs from catch rate. Team totals and player props are context with their own dates and coverage. They are not additional projection-provider votes.

## Reuse boundary

The bundled `fantasy_core` handles identity, evidence, news, roster valuation and session integrity. Future skills can import those contracts. Their weekly or waiver-specific scoring and freshness requirements remain separate. Version saved schemas and test the ZIP from outside the repository before releasing changes.

## Executable public adapters

`prepare_data.py --league league.yaml --season 2026 --fetch-espn --fetch-cbs --fetch-fantasypros --out players.csv` attempts all three providers. Use the requested season rather than copying this example year. ESPN establishes provider identities; CBS and FantasyPros tables are matched conservatively, with unmatched/ambiguous rows quarantined. FantasyPros public coverage may be truncated and consensus constituents unverified. Provider update time may be unavailable; the report then remains limited even after a successful fresh download.

Use `--projection-import manifest.json` for an authorized stat CSV with explicit field mappings and provenance. No provider login or paid-data bypass is included. `--as-of` enables reproducible offline checks, not a claim that a historical file is current. Defaults reject projections older than three days when their update date is known. Fetch results and field coverage determine readiness per player; merely requesting three sources does not establish three usable forecasts.

`assets/example-evidence.json` and `assets/example-evidence-league.json` form a one-player synthetic preparation example. Pass `--as-of 2026-09-06T12:00:00Z` to reproduce its scored output. It demonstrates the evidence contract, not a complete draft pool.
