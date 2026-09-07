# Changelog

## 3.0.0 — shared evidence, roster coverage and local live advice

- Added a self-contained shared core for player identity, dated multi-source stat projections, explicit missing data, source independence and superseding news. Public/import adapters preserve provenance; incomplete data is labeled or rejected rather than silently called consensus.
- Default draft utility now includes legal starter strength and modeled absence coverage, with explicit replacement and optional performance-upside assumptions. Source disagreement is not treated as performance volatility. Legacy policy remains for historical examples.
- Added local live sessions with confirmed picks, undo/replay, keeper ownership, revisions, source refresh, conditional next-turn comparisons and auditable evidence-bound decision receipts. Static HTML remains preparation mode.
- Added a held-out one-pick evaluation harness; no real-season improvement claim accompanies this release. The old 800-draft benchmark is explicitly historical.
- Added reproducible ZIP packaging, installed-package tests and CI. The bundle includes its reusable Python core; lineup, waiver, dynasty and auction engines remain future work.


## 2.0.1 — correct late-round availability

- Fixed late-round recommendations promoting early targets and watched players despite zero modeled availability. Tables beyond the rollout horizon now apply the simulator’s existing 15% availability floor, including expanded rows and notes-added players with known availability.
- Added current-pick availability to late rows and renamed “vs. free” to “vs. starter”: the metric is a projected starting-lineup benchmark, not waiver value.
- Added regression tests covering unavailable reference rows, notes reintroducing players, and preservation of evaluated early-round falls. Rebuilt the public sample and reran its 800-draft benchmark.
- **Upgrade:** replace the installed v2.0.0 skill with v2.0.1 and rebuild your HTML board using your saved league, players, simulation and notes. Existing HTML files do not update automatically. This fix does not require a new player-data download or simulation.

## 2.0.0 — simulate draft continuations, deliver a usable plan

For each candidate at a pick, the engine simulates the remaining draft and scores one best legal starting lineup using saved season projections. These continuations are called rollouts. They help explore roster construction instead of relying only on a player's isolated rank or projected surplus.

### Why the method changed

Earlier versions ranked picks directly by surplus above an assumed replacement level. Two plausible replacement assumptions produced opposite plans with the same projections: one drafted eight running backs, another took receivers in rounds two and three. That prompted the shift to scoring the resulting lineup. Replacement still affects candidate shortlisting and continuation heuristics; the new method does not eliminate assumptions.

### Draft board

- Prepared targets appear first, with alternatives and signed differences in conditional modeled lineup estimates. Small rounded differences are labeled close, not statistically equivalent.
- A configurable availability floor chooses realistic plan targets while retaining rarer upside candidates.
- Every actual pick has a table. Expanded rows, roster eligibility rules and a complete saved fallback order are shared with the benchmark through `board_policy.py`.
- Manual taken/my-pick tracking, undo, saved browser state, print, tier boards and the lineup strip remain available. Marking players does not recalculate the estimates or sync with a draft platform.
- `At [pick]` explicitly means unconditional pre-draft availability. It is not the probability a player survives after being available now and passed over. Rounded extremes show <1% and >99%, without implying certainty.
- The cost-of-waiting table describes the modeled change in best available positional surplus between picks. Replacement cancels in that subtraction for fixed states, but changed model assumptions can change the draft paths.
- Mobile controls have 44px targets, long verdicts wrap, and the public sample includes links back to personal setup and GitHub.

### Model and benchmark corrections before launch

- All keepers now occupy their owners' rosters and consume a valid round. Published lists use explicit draft slots rather than order-of-appearance mapping.
- Scope is zero or one keeper per team. Unsupported multi-keeper inputs, duplicate ownership and invalid costs fail early.
- Keeper scenarios run before board generation. Automatic selection uses the best evaluated scenario; explicit user overrides remain authoritative. The automatic shortlist is not an exhaustive keeper search.
- The benchmark follows the delivered board's saved ordering and documented fallback. Both the board and noisy ADP baseline use the same eligibility and starter-completion rules.
- The corrected 800-draft benchmark replaces the earlier 109-point claim, which used a different policy and a baseline that could leave starting slots empty. Current results, paired intervals, complete-lineup counts and source hashes are in [benchmark.json](examples/sample-league/benchmark.json).
- Invalid player names, nonfinite inputs, unsupported positions, impossible roster capacities and nonpositive simulation settings fail before expensive runs.

The score is the sum of projections for one best legal starting lineup. It does not simulate weekly substitutions, injuries, bench coverage, waiver activity or playoff wins. Matched controls reduce some draft-sampling variation; they do not make differing availability populations exactly comparable. Monte Carlo intervals do not represent total projection/model uncertainty. The legacy `within_noise` fields remain descriptive heuristics, not equivalence tests.

### Launch experience and security

Added an account-free sample homepage, reproducible paired draft example, captioned 26-second board demonstration, deliberate poster, social cards and guided setup. The mobile comparison shows the changed result next to its choice controls. Repeated benchmark claims are generated from machine-readable evidence.

The renderer escapes plain text and embedded JSON, validates custom colors, and restricts rich-text fields to formatting-only tags without attributes. The packaged skill includes the shared board policy. Tests cover injection boundaries, keeper ownership, input validation, displayed/benchmarked order, and roster completion.

### CLI and scope

Rollout controls include `--pick-values`, `--no-pick-values`, `--rollouts`, `--candidates`, `--through-round`, `--plan-min-avail`, `--keeper-scenarios`, `--watch`, and `--strict`. `--sample-links` adds public sample navigation when rendering. Runtime depends on simulation settings and hardware; full analysis takes several minutes.

Snake and linear draft order are supported. Auction bidding is not implemented; the methodology describes a separate budget-allocation approximation. TE premium must be applied when scoring the input projections; the simulator warns if the setting is present. Superflex and FLEX use the configured legal slots. The adaptive continuation heuristic still delays K/DEF until its last two rounds; the prepared board's explicit late targets and its benchmark can differ from that heuristic.

New simulation keys include `pick_values`, `plan_path`, `cost_of_waiting`, `keeper_scenarios`, `plan_check`, and `rollout_settings`. The saved sample remains dated analyst-authored data; generating a personal board requires fresh source checks.
