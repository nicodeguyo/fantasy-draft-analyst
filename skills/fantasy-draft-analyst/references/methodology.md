# Methodology

Use this reference before producing a draft plan. The objective is to help a user explore what a pick does to the rest of their draft, using explicit league rules, projections, and opponent assumptions.

## 1. Price this league

Use projections scored for the user's lineup and scoring rules, and ADP (average draft position) from the closest available platform and format. Keep source dates. A descriptive note about a QB-happy league does not automatically change simulator behavior: either encode a supported input change and rerun, or present the tendency as an unmodeled sensitivity.

## 2. Pick value by rollout

For each pick and candidate:

1. Simulate the draft to that pick, including keeper ownership and forfeited picks.
2. Branch from the saved state when the candidate is available.
3. Draft that candidate and let a lineup-aware heuristic complete the roster.
4. Score roster utility: legal starter strength plus explicit absence coverage and optional performance-upside assumptions. `preferences.draft_policy: legacy` retains the old fixed-lineup policy for historical reproduction.
5. Compare this result with an unforced continuation from the same state.

The reported estimate is `mean(all controls) + mean(candidate − matched control | candidate available)`. It estimates a candidate's contribution on states where that candidate was available, then adds the common control mean to retain modeled roster-utility units.

**Shared randomness.** Candidates share the prefix state and copied random-generator state. Later picks can diverge, and candidate removals can change which players receive later random draws. This coupling reduces some simulation variation; it does not imply identical opponent decisions throughout each branch.

**Conditional samples.** A rare fall can happen in a different kind of draft from a common availability. Matched controls reduce additive board effects, but cannot guarantee comparable candidate effects across different availability populations. Candidate-by-board interactions can change rankings. Increasing rollouts reduces Monte Carlo noise, not that modeling bias.

**Uncertainty.** `se` describes noise in the candidate-minus-control estimate under fixed inputs. It excludes projection error, opponent-model error, and uncertainty in the common control mean. The board labels an absolute gap below one projected point “close” as a rounding convention, not a standard-error test or proof of equivalence. Use “no clear model preference” for small differences, especially with low `n`. Shared candidates require covariance-aware paired contrasts for formal inference; selecting a winner also introduces selection uncertainty.

**Read within a pick.** Each pick has its own control population and assumed earlier plan. Compare candidate estimates within the pick with the above limitations. Do not subtract across pick tables or compare their values directly with keeper-scenario totals. A target must meet the configured availability floor (50% by default); the target is promoted to the first displayed row, and better but less available candidates are shown as upside alternatives.

**What performance means.** `scripts/compare_policies.py` compares the displayed board policy, a noisy ADP-based draft bot, and the simulator's adaptive policy. The board follows displayed order, including expanded rows, obeys configured exclusions and position caps, and reserves remaining picks for unfilled starting slots. When its displayed candidates are exhausted, it uses the documented shared surplus fallback. Written late targets must be part of that displayed policy. Use results generated from the current sample and code; the historical experiment predates the keeper and policy-alignment repairs.

Report mean projected-lineup points and the paired benchmark difference with its stated interval. This is an internal model comparison, not a real-draft backtest or a comparison with actual ESPN autopick. Variation across draft simulations is draft-model variation, not season consistency. The score omits weekly lineup changes, injuries after drafting, byes, waivers, and the insurance value of bench players. A backup can be useful in fantasy while adding zero to this particular fixed-lineup objective.

The continuation heuristic and candidate shortlist still use replacement-based surplus. Their assumptions can change the explored candidates, later roster construction, and rankings. Scoring final lineups reduces direct dependence on replacement; it does not eliminate all dependence or establish that rankings survive policy bias. Test sensitivity and benchmark the delivered policy on separate seeds.

## 3. Replacement level and surplus

`surplus = projection − replacement[position]`. Replacement is an estimate of the marginal starter's projection, not a promise that a player with that score will be available on waivers.

Flex-equilibrium calculation:

1. Allocate each position's dedicated starting slots league-wide.
2. Allocate flexible slots to the strongest eligible remaining players.
3. Add the configured allowance for depth/bye coverage.
4. Use the marginal allocated player at each position as replacement.

Read `flex_fill` and the replacement output for this league. A cliff in projections can make a small rank change move every player's surplus substantially. The earlier eight-RB failure motivated scoring complete lineups instead of directly sorting every pick by surplus. Surplus remains useful for describing depth and for the engine's candidate/fallback choices.

## 4. Keeper decisions

The simulator supports **zero or one keeper per team**. Every keeper consumes one valid round. Multi-keeper combinations, traded pick costs, and auction keeper budgets are outside this implementation.

A published `league_keeper_list` entry has `draft_slot` (one-based original draft position), `player` (exact CSV name), `round` (pick cost), and optional descriptive `team`. Use unique player names and draft slots. A non-empty supplied list is complete for opponents: omitted teams keep nobody. An empty list means unknown opponent keepers and uses modeled draws. An entry for the user's slot does not override the keeper being evaluated by the CLI.

With `--keeper-scenarios`, the engine evaluates up to four eligible candidates shortlisted by isolated surplus plus keeping nobody, **before building the board**, and automatically selects the highest simulated mean. `--keeper NAME` and `--no-keeper` retain explicit user control. Without scenario evaluation, automatic selection uses positive isolated surplus. The shortlist is not an exhaustive search of all eligible keepers; manually evaluate a relevant omitted candidate rather than claiming global optimality.

Lead with separate full-draft scenario scores and their Monte Carlo uncertainty. Then explain cost (round converted to the user's pick), platform ADP, projected points, and surplus relative to what that pick could buy. Surplus explains the decision but does not replace the scenario comparison.

Keeper removals thin the pool; forfeited picks partly offset that effect later in the draft. Read simulated inflation at each pick rather than adding the keeper count to every pick. Confirm eligibility, escalation, and waiver-acquisition rules before selecting. Next-year keeper optionality is useful football judgment but is outside the one-season score.

## 5. Pick geometry

For a snake draft with `N` teams and slot `s`, round `r` is `(r−1)N+s` for odd rounds and `rN−s+1` for even rounds. Linear drafts use `(r−1)N+s` throughout. Remove keeper-forfeited turns. Long gaps at the turn make fallback depth useful; middle slots permit more frequent decisions. Explain actual pick numbers, not a generic “round three” recommendation.

## 6. Pre-draft availability and the analytical shortcut

The simulator measures how often a player remains undrafted immediately before each user pick across all modeled drafts. The user's seat also drafts using the ADP-based market policy during this availability pass. `avail_pct` and `next_pct` are **unconditional pre-draft frequencies**.

Say “available before pick 29 in X% of simulated drafts.” They are not the probability that a player survives after the user sees him available and deliberately passes on him. The user may draft him in some simulated paths, which also removes him from later availability. Tapping the board does not update these estimates. Finite-sample 0% and 100% do not establish impossibility or certainty.

A proper live pass-up probability would branch only from current states where the player is available, force an alternative pick, and simulate intervening opponents. This implementation does not estimate that quantity. Use pre-draft frequencies to prepare alternatives and understand typical windows, not as a stand-alone “take now or lose him” rule.

The opponent policy combines noisy ADP with positional-need and K/DEF rules. It is not a calibrated replica of a platform's autopick or a known distribution of real managers. Evaluate plausible alternative room assumptions when a recommendation depends on them.

Without scripts, a rough normal approximation is `P(available at p) ≈ 1 − Φ((p_eff − ADP)/σ_eff)`, where effective pick includes a stated keeper-inflation approximation. Label this as an analytical estimate; a normal approximation to ADP is not validated live survival probability.

A chat-only decision can compare a candidate's projection with the best same-position alternative expected one turn later, then account for open roster slots. This dynamic-VBD approximation sees only one turn and has not been established as equivalent to the full rollout method. State the method actually used.

## 7. Tiers and cliffs

Build tiers from projection gaps within a position, keeping role and projection uncertainty visible. A useful starting rule is a gap of at least eight points and 1.5 times nearby gaps, but do not treat the rule as statistical evidence. Label actual point drops and broad ADP windows. Within a close tier, consider roster need and role certainty; lower pre-draft availability suggests a narrower expected window but does not settle a live decision.

## 8. Scarcity by position

Recompute for the current pool. Deep WR groups, thin RB workloads, and concentrated elite-TE value are hypotheses to check, not fixed draft orders. One-QB formats often allow later quarterbacks; a particular projection or scoring system may justify an earlier pick. Superflex and two-QB lineups change demand substantially. Explicit league scoring belongs in player projections before simulation.

## 9. Reach rules

Explain the opportunity cost of taking a player early relative to ADP. Evaluate role certainty, alternative targets, available starter slots, and the next gap between picks. Refresh injury and depth-chart sources before a reach. Avoid mechanical rules based only on an unconditional next-pick percentage.

## 10. Build projections you can defend

Start from sourced stat lines and score them in the league's settings. Date every input. Adjust projections only with an explicit reason: role changes, expected games, efficiency regression, or team context. Keep source facts separate from analyst assumptions. If data is unavailable, identify the gap; sample inputs are saved examples, not a current consensus feed.

Expected-game discounts may already be built into season totals. The v3 coverage model uses separately declared expected games and projection conventions to avoid multiplying that discount twice. Its absence scenarios are an approximation, not a full simulated schedule. Run sensitivity cases for the projections driving the recommendation. A tight Monte Carlo SE can coexist with a badly wrong player projection.

## 11. Cost of waiting and sample drafts

`cost_of_waiting[pick][pos] = E[best surplus available now] − E[best surplus available next turn]`.

The shared replacement constant cancels in the direct subtraction, but changed assumptions can affect simulated paths and hence the output. Interpret this as modeled loss of available positional talent over a draft interval, not a guaranteed cost of a live decision. Roster fit still matters: the biggest positional drop does not automatically identify the best player for an already-filled lineup.

Use the current output to describe the strongest positional windows. Sample drafts illustrate possible rosters; report which policy produced them, their separately labeled starter-point and roster-utility ranges, and repeated choices. A few examples do not establish a general performance distribution. The target plan should include reachable alternatives, not depend on the best observed lucky fall.

## 12. Late rounds

Useful bench picks can provide injury cover, a path to a larger role, or future keeper value. The v3 utility scores coverage under declared absence and waiver assumptions, and optional upside only from explicit performance uncertainty. It does not value future keeper years. Explain unsupported considerations separately.

The displayed board policy is authoritative for a board-following benchmark: follow its ordered candidates, including expanded rows; skip configured exclusions or full position caps; reserve enough picks to fill the starting lineup. If its candidates are exhausted, use the shared surplus fallback shown in the board. Put any specific late-round target into the displayed plan so a benchmark and the user receive the same instruction. The adaptive rollout heuristic is a separate policy and may reserve K/DEF for its final picks.

## 13. Superflex, 2QB, TE-premium, best ball, auction

Superflex and two-QB slots change legal lineup scoring and demand; recompute rather than multiplying QB value by a fixed factor. TE-premium must be reflected in the input projections. Confirm the scoring helper's supported fields for custom bonuses.

Best ball requires weekly scoring and is outside the fixed-season-lineup objective. Dynasty requires multi-year player value. Auction requires a bidding model; the pick simulator rejects auction mode. A surplus-to-budget allocation can be offered as a separately labeled approximation, not as an auction simulation.

### Auction

The pick simulator rejects `draft_type: auction`; it does not model nominations, bids, opponent budgets, or auction keeper inflation. For auction users, offer a separately labeled **pricing approximation** only:

1. Confirm each team's budget, roster size, minimum bid, scoring, and any kept players and costs.
2. Reserve the minimum bid for every remaining roster slot, then calculate the remaining discretionary league budget.
3. Define the available draft pool and replacement assumptions. Allocate that discretionary budget in proportion to positive projected surplus among the players expected to be drafted, adding the minimum bid to each price.
4. Check that the resulting prices sum to the stated remaining league budget. Show how alternative projections, player pools, and replacement assumptions change the prices.

These are budget-allocation estimates, not predicted clearing prices or a validated bidding strategy. Keeper leagues need explicit remaining budgets and an available-player pool after keepers; the snake-draft keeper scenarios do not supply that auction calculation. Direct users who need bidding or nomination advice to an auction-specific model.

## 14. Sensitivity

Name the assumptions most likely to change the pick: important player projections, opponent ADP/needs, keeper eligibility, roster rules, and continuation/fallback policy. Change plausible inputs and rerun when a decision is fragile. Replacement assumptions can still affect shortlisting and continuation. The deliverable should let the user disagree with a specific assumption and understand what to test next.

## 15. Player research

Check role, route/snap share, earned targets, team volume, red-zone opportunities, and expected games using dated sources. Treat small samples and camp quotes cautiously. Betting lines can be a cross-check with their own assumptions; they are not automatically player medians or proof of a projection. See `metrics.md` and `data-sources.md` for research guidance, verifying current availability rather than treating older source descriptions as a live audit.

## v3 metric and evidence contract

`sim.settings.draft_policy` and `sim.roster_utility` identify the objective. `totals` retains starting-lineup points for compatibility; candidate comparisons under `roster_v2` use utility and must be labeled accordingly. Do not compare utility values to the archived v2 projected-point benchmark.

The coverage model uses explicit expected games when supplied; otherwise it declares its missed-game default. A separately configurable waiver baseline determines how much a bench player adds. Its default positional cutoff is conservative and is not a measured waiver pool. FLEX and superflex assignment never count a player twice. Expected source disagreement (`projection_sd`) is separate from performance uncertainty (`performance_sd`).

For live recommendations use confirmed draft state, not unconditional pre-draft availability. See `live-draft.md`. For normalized stat lines, source status and dated news see `evidence.md`. Run source and role sensitivity before recommending a large ADP reach; explain take-now versus a feasible alternative next turn and the assumption that could reverse the choice.
