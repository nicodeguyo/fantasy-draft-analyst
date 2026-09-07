---
name: fantasy-draft-analyst
description: Research and plan NFL fantasy drafts using league-scored multi-source evidence, keeper scenarios, roster-aware simulations and draft boards. Use for snake or linear draft preparation, pick comparisons, live manual draft assistance, player pressure tests and post-draft review. Supports zero or one keeper per team; weekly start-sit and waiver decisions are separate workflows.
license: MIT
metadata:
  version: "3.0.0"
  author: "Nico Neugebauer"
  homepage: "https://github.com/nicodeguyo/fantasy-draft-analyst"
---

# Fantasy Draft Analyst

Recommend the player who improves this roster at this price. Show the evidence, the alternative and the assumption that could reverse the recommendation. A strong starting lineup, usable depth and reliable draft state all matter.

Read [methodology](references/methodology.md) before quantitative analysis. For data preparation, read [evidence](references/evidence.md) and [data sources](references/data-sources.md). For a board that recalculates during a draft, read [live draft](references/live-draft.md). These references describe executable contracts, not permission to access private accounts or submit picks to a platform.

## 1. Establish league and decision context

Collect platform, season/draft date, teams, slot/order, rounds, scoring, mandatory/FLEX slots, bench capacity and keeper rules. Ask for unresolved material facts together; retain confirmed facts between runs. `league.example.yaml` describes the supported configuration. Check that rounds and roster capacity agree.

Record keeper owner and exact consumed pick separately. Use confirmed declarations; unknown opponents are explicitly modeled scenarios, not facts. A future-round keeper is already owned and unavailable. The current model supports zero/one keeper per team; identify unsupported variants before simulation.

For live work, collect actual picks and the user's actual roster. A missed or unknown player still consumes its original pick. For post-draft review, reconstruct the complete supplied draft, distinguishing keepers from open selections. Do not critique passing on someone already gone.

## 2. Prepare current, traceable evidence

Use `scripts/prepare_data.py` and its `--help` with a dated evidence snapshot. Provider adapters and file imports preserve source stat lines, identity, season/period and timestamps. The output includes a league-scored player CSV and an evidence report. The shared `scripts/fantasy_core/` package ships inside this skill.

Before using the output, inspect errors, coverage, mode, unmatched identities and dates. Source count means usable estimates for this player, not sites visited; the separate verified independent-source count tracks documented independence. A consensus and its constituents may overlap. Missing or malformed required statistics are unresolved data, not zero production.

Use stat-line projections for production, platform ADP for price, usage for role plausibility, news for changed circumstances and betting lines as cross-checks. Preserve individual estimates and disagreement. Weekly, season and rest-of-season forecasts are different periods. Confirm custom scoring support before claiming exact rescoring.

Refresh actionable injury/role news for shortlisted candidates near the draft. Store original source, event time, publication time, evidence quality, conflicts and superseding updates. A projection adjustment must name its affected workload/games assumption and supporting event. Check whether the provider already included it; apply an injury discount once. Generic positive sentiment is not a point adjustment.

Research depth should fit the clock: prepare the broad pool before the draft, use cached validated data for immediate picks, and refresh targeted evidence without blocking a legal fallback. Source endpoints can fail; a failed source is a visible coverage gap.

**Modes:** full projection evidence supports quantitative comparisons; limited evidence requires explicit caveats; rank-only evidence supports structural/tier advice without fabricated point gaps. Legacy `players.csv` remains usable but does not establish fresh multi-source evidence. Saved examples are never current-data substitutes.

## 3. Compare draft paths

Run the bundled simulator after the evidence and settings are coherent:

```bash
python3 scripts/draft_sim.py --league league.yaml --players players.csv \
  --sims 1500 --pick-values --keeper-scenarios --out sim.json
```

Use `--help` for supported controls. Explicit keeper/no-keeper choices override automatic selection. Read `plan_check` before presenting a plan. When candidate shortlists exclude a relevant option, evaluate it rather than imply exhaustive optimization.

The default roster-aware objective includes explicit coverage/upside assumptions; report its score as **roster utility**, separately from projected starting-lineup points. Legacy policy is available for historical comparison. Simulation sampling error, source disagreement, football outcome risk and draft-price dispersion are different uncertainties. A small Monte Carlo error is not proof of a strong football preference.

Show take-now/wait/pivot alternatives at actual pick numbers. Pre-draft availability is an unconditional simulation frequency, not the chance a currently available player survives a deliberate pass. Read the live output's method before describing live urgency or survival. Explain a reach with role evidence, roster need, next-pick alternatives and sensitivity—not ADP alone.

## 4. Deliver the right board

**Preparation board:** `scripts/build_board.py` creates a portable HTML from league, player, simulation and notes files. Its values are frozen; marking players changes visibility, not the original simulation. Use the [output specification](references/output-spec.md) for notes and presentation.

**Live local board:** `scripts/live_draft.py` keeps versioned picks and recalculates through the shared decision policy. Initialize from actual league/player inputs; launch its loopback server as described in [live draft](references/live-draft.md). This needs Python on the machine serving the board. A downloaded HTML alone cannot start that engine. It does not submit real platform picks.

State corrections, undo and projection refresh must preserve the draft history. Use exact event identifiers and revision checks. A recommendation for an older revision is stale; recalculate before naming it current. Preserve unknown picks and resolve their identity without shifting subsequent picks.

Keep explanations within available player IDs and supplied evidence. If an explanation fails validation, use the deterministic shortlist and state the limitation. Never invent current facts to justify the engine's preference.

## 5. Explain the decision and pressure-test it

Lead with the recommendation, then the best alternative and confidence. Show starter improvement, coverage and useful upside separately when available. A seventh receiver must justify its marginal benefit against another usable RB; avoid fixed universal roster-count rules.

For each disputed player, use [metrics](references/metrics.md): verify the premise, cite relevant usage with sample size, identify the main failure case, check available market evidence, and conclude at the user's actual price. A prop is not a ceiling. Historical touchdowns alone do not establish a current role.

Show source dates, adjustments and assumptions in an expandable appendix. Distinguish observed statistics from projections and judgment. Compare candidates within a pick; keeper scenarios and different pick contexts are separate experiments.

## 6. Verify and preserve the result

Check no drafted/kept player appears as available, one player occupies at most one lineup slot, required starters can be completed, and source season/scoring agree. Keep league inputs, evidence snapshots, simulation settings and live decision records in the user's output directory outside the installed skill.

For a fresh run, compare snapshots: changed facts, changed assumptions, changed recommendations and unchanged decisions. For post-draft grading, separate expected roster strength, acquisition price, keeper subsidy, depth and uncertainty. Give a rubric and tiers for close teams; rankings alone do not determine letter grades.

Use historical evaluation only with as-of inputs and consistent lineup/waiver policies. Report missing historical data and unvalidated assumptions. Internal simulated drafts are not proof of a real-season advantage. Future lineup/waiver skills may reuse the core evidence and scoring, but require their own decision models.
