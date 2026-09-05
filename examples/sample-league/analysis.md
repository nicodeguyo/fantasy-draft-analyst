# Sample League: a draft plan you can inspect

**Explore what your next pick does to the rest of your draft.** This fictional example uses 12 teams, ESPN half-PPR scoring, pick 5, one flex, and one same-round keeper per team. Player inputs are saved from September 3, 2026; they are not a live feed or personalized advice.

[Open the generated board](draft-board.html) to see current targets, alternatives, and model values. The board is the authoritative source for numerical recommendations; this guide explains how to use them without duplicating numbers that can become stale.

## Start with the keeper comparison

The scenario pass evaluates up to four eligible candidates shortlisted by isolated surplus plus keeping nobody. It selects the highest simulated mean before preparing the board, unless a keeper or none is explicitly chosen. Compare the scenario table on its own scale; a pick-table value has a different control population.

The model includes keepers on their owners’ rosters, removes them from the pool, and forfeits their round costs. Confirm real keeper eligibility and ownership before generating a plan for your league.

## Read one pick at a time

The prepared target appears first with TAKE. Other rows show the estimated projected-lineup difference from that target. A rare higher-value alternative can be useful when it falls, while a lower gap may justify preferring a role or roster fit you trust more.

Expand the alternatives if needed. Follow displayed order, skip configured exclusions and full position caps, and reserve enough remaining picks for unfilled starting slots. If displayed candidates run out, use the board’s documented shared surplus fallback. The benchmark uses this same policy, including written late targets.

## Use the positional view to prepare

The cost-of-waiting table shows the modeled drop in available talent between your turns. It helps identify narrower positional windows. The biggest drop does not automatically identify your best pick: your already-drafted players and remaining slots matter too.

Availability is the fraction of all modeled drafts in which a player is undrafted before a pick. It is useful pre-draft context, not the probability he survives after you deliberately pass on him while he is available. Marking players does not recalculate these frequencies.

## Understand the score

The model sums season projections for one best legal starting lineup. It does not simulate weekly substitutions, byes, new injuries, waivers, or bench insurance. A backup may be useful in a real league even if this score gives that pick no additional points.

Small gaps indicate limited model preference. Candidate populations can differ, the continuation heuristic influences results, and Monte Carlo standard errors exclude uncertainty in projections and opponent behavior. Challenge the important inputs, then rerun plausible alternatives.

## Bring it to draft night

Open the HTML board before drafting and try its controls. Tap a player to mark another team’s pick; use the checkmark for your pick. The roster updates locally and browser storage preserves marks when available. These are tracking controls, not live simulation or a connection to ESPN.

Read the [source record and reproduction steps](RUNLOG.md) for provenance and the [methodology](../../skills/fantasy-draft-analyst/references/methodology.md) for the statistical contract. New league plans require current sourced inputs.
