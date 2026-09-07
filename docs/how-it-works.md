# How the draft advice works

Your scoring rules and roster slots determine what useful production means. Player data enters the shared evidence layer, which checks identity, season, period, scoring completeness and dates before scoring each provider's stat line. ADP describes draft price; it is not a projection. Multiple websites may repeat one upstream forecast, so provider count and independent-source count are separate.

The draft engine ranks decisions by modeled roster utility: a legal starting lineup, additional coverage during explicit absence scenarios, and an optional upside term only when a separate performance-uncertainty input exists. Projection-source disagreement and ADP spread never stand in for performance uncertainty. Defaults and replacement assumptions appear in outputs. Utility is neither predicted season points nor win probability.

Preparation mode simulates possible remaining drafts. Its saved HTML board stays a prepared plan when marked. Live mode replays confirmed picks, assigns players to actual team rosters, removes drafted players, and calls the same roster policy. Bounded paired simulations compare taking a candidate with alternatives at the next real turn. Those trials describe the opponent model; their survival rates are not calibrated probabilities of your room.

Every live recommendation has a versioned receipt with data/state references, candidates and an evidence packet. Explanations must match that packet. Unknown picks preserve consumed draft slots but reduce what can be inferred about rosters. Updating source data creates a new revision; old receipts remain inspectable.

News and betting markets are evidence checks. They do not add arbitrary points to the score. A role-change adjustment needs an explicit assumption and rerun. Betting lines require date, market, book, prices and settlement context; a yards prop is not a complete fantasy projection or a ceiling.

The archived v2 benchmark scores one fixed starting lineup and does not validate v3. The new evaluator compares pre-decision policies using held-out snapshots, then selects weekly lineups from forecasts timestamped before lock. It reads realized outcomes only after selection. This is a bounded one-pick evaluator, not a complete season, waiver or championship simulator.

See the [shared architecture](toolkit-architecture.md), [methodology](../skills/fantasy-draft-analyst/references/methodology.md), and [evidence contract](../skills/fantasy-draft-analyst/references/evidence.md).
