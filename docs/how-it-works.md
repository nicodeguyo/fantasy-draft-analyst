# How the draft board works

**Don’t just rank players. Explore what your next pick does to the rest of your draft.**

A player ranking evaluates names. This tool asks a second question: if you take this player, what starting lineup could you finish with after everybody else keeps drafting?

## From your league to a plan

1. **Describe your league.** Scoring, roster slots, draft order, and keeper costs determine which choices matter.
2. **Collect player inputs.** The assistant sources ADP—average draft position—and projections, records dates, and scores projections under your rules.
3. **Explore draft continuations.** For a candidate at your pick, the simulator saves a possible draft state, takes that candidate, and completes the draft using a lineup-aware drafting policy. It repeats this process across many states. These continuations are called *rollouts*.
4. **Compare the resulting lineups.** The score adds the season projections of one best legal starting lineup. A matched continuation with no forced candidate helps account for favorable draft states.
5. **Bring the board to your draft.** Use its ordered choices and fallbacks, mark taken players, and log your own picks. These marks do not recalculate the saved recommendations.

## Read a pick table

`TAKE` identifies the prepared target. A signed gap compares another candidate with that target under the model. For example, `−14` means an estimated 14 fewer projected points in the fixed starting lineup—not a measured loss of 14 points in your actual season. A small gap may mean there is no clear model preference.

A target must meet the configured pre-draft availability floor. A stronger candidate who appears less often may remain an upside alternative. The displayed order, including expanded rows and its documented fallback, defines the policy tested by the board benchmark.

Candidates share saved draft states and random seeds where possible, but later picks can diverge. A candidate is scored only where available, so rare and common candidates can have different sample populations. Matched controls reduce some board-luck effects without eliminating every bias. Standard errors describe simulation noise under fixed inputs; they do not measure uncertainty about a player's role or future season.

## Understand availability

“Pre-draft availability at pick 29” means the fraction of modeled drafts in which a player is undrafted immediately before that pick. The user's seat drafts from the ADP-based market policy in this pass too.

That is useful for preparing fallback targets. It does **not** answer “I can see him available now; if I take someone else, will he survive?” Answering that would require conditioning on the live board and simulating a specific alternative pick. The current board does not do that. A saved 0% or 100% is a finite simulation frequency, not certainty.

## See the cost of waiting

The positional table compares the best available projected talent now with the best expected at your next turn. It helps reveal windows where a position tends to thin out. It does not automatically tell you which player to take: roster fit and the remaining draft still matter.

Replacement level—the estimated projection of a marginal starter—cancels in the direct subtraction. It still influences some candidate and continuation choices, so changing it can change draft paths. The engine reduces direct reliance on this assumption rather than making it irrelevant.

## Compare keepers

The simulator supports zero or one keeper per team, each costing a round. Known keepers are assigned to explicit draft slots and occupy their owners' rosters. A non-empty supplied keeper list is complete; omitted opponents keep nobody. An empty list means unknown keepers and uses modeled draws.

With keeper scenarios enabled, the engine compares up to four eligible candidates shortlisted by surplus, plus keeping nobody, before building the board. It chooses the highest simulated mean unless the user explicitly selects a keeper or none. A relevant candidate outside that shortlist needs a separate evaluation; this is not multi-keeper optimization.

## Measure the strategy

The reproducible benchmark compares the prepared board policy, a noisy ADP-based draft bot, and the simulator's adaptive policy. Different player ordering and late-round choices are part of the strategy's value. The tested board policy must match the instruction delivered to a user, so those differences are measured deliberately.

This is an **internal simulation comparison** using shared player projections and an opponent model. The ADP bot is not a verified replica of ESPN or another platform's autopick. Shared seeds couple randomness, while later rooms can diverge after different choices. Use the current generated benchmark output; historical results from earlier policies are not interchangeable.

The fixed-lineup score does not simulate weekly substitutions, byes, new injuries, waivers, or playoff wins. A backup may add no score while still providing real insurance value. Lower variation across simulated drafts means more similar modeled rosters, not more consistent real seasons. The benchmark is useful evidence about this model, not a promise of fantasy points.

## Why this approach exists

Two early versions built opposite draft plans from the same player inputs; one drafted eight running backs. Changing the assumed replacement level had changed the answer. That motivated evaluating complete projected lineups rather than simply sorting players by surplus.

The method still depends on projections, which candidates are explored, and how later picks are made. Its value is making those choices inspectable: change an input, rerun the model, and see whether the recommendation survives.

The [sample run log](../examples/sample-league/RUNLOG.md) records saved input provenance. The [technical methodology](../skills/fantasy-draft-analyst/references/methodology.md) explains estimators and limits, and the [reproduction guide](install.md#running-the-scripts-yourself) shows how to run the same process.
