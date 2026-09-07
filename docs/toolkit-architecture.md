# Shared fantasy toolkit foundation

The draft skill is the first consumer of a reusable Python core, bundled under `skills/fantasy-draft-analyst/scripts/fantasy_core/`. Keeping it inside the skill makes the ZIP standalone; future skills can package the same versioned core without external relative imports.

The shared boundary includes canonical player identity, provider evidence, news history, league scoring, roster utility and durable decision state. Season, weekly and rest-of-season projections remain distinct. The draft workflow owns ADP, keeper cost, pick availability and roster construction. Future lineup and waiver skills need separate matchup, lock-time, transaction and acquisition-cost models.

## Design decisions

- Provider stat lines remain inspectable after aggregation. Different publishers may have overlapping estimates; source independence is explicit.
- Missing/malformed required values are validation failures, not football zeros. Legacy sparse CSV scoring remains an explicitly limited compatibility path.
- Expected starting-lineup points are distinct from roster utility. Depth and upside assumptions are exposed and are not calibrated championship probabilities.
- ADP dispersion models draft-price uncertainty; independent performance uncertainty is a different field.
- Draft events and player-data revisions are independent. Refreshing projections cannot delete selections. Unknown picks retain their original slots.
- Immediate recommendations use local validated data and deterministic logic. Explanations refer only to available players and recorded evidence.
- Downloaded preparation HTML is static. The local live board requires its Python engine; both modes identify their limits.

## Evaluation

Correctness tests cover identities, source periods, scoring, roster legality, keeper ownership, event replay and packaging. Behavioral tests exercise CLI and HTTP interfaces. Internal draft-room comparisons use common seeds and documented baselines; they are not real-season backtests. Historical evaluation requires as-of forecasts and availability, consistent lineup decisions and a separate development/held-out split. Realized weekly points must never select that same week's starters.

## Distribution and contribution

Run `python scripts/package.py` to build the deterministic ZIP. CI runs tests on supported Python versions and checks that the committed download matches source. Private league sessions and licensed provider exports stay user-local. Provider adapters may support authorized imports without redistributing their data.

Build new workflows against the shared contracts when they have real inputs and tests. Weekly start/sit, waivers, auctions and hosted multi-user services are outside this release's draft scope.
