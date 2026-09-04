# Changelog

## 2.0.0 — pick values by rollout

**What changed.** The skill used to rank every pick by *surplus* — a player's projection minus the
"replacement level" at his position. That baseline is chosen, not measured, and this year it lands on
a cliff in the running-back projections (RB37 projects 132, RB40 projects 111). Two defensible ways of
drawing the line produced opposite plans for the same league from the same projections: one drafted
eight running backs, the other took receivers in rounds 2 and 3. When the answer swings that far on a
parameter nobody can pin down, the parameter is doing the deciding.

So v2 asks the question directly. At each of your picks, for each candidate, it plays the rest of the
draft out and adds up the starting lineup you end with. That number is **pick value**, and it needs no
baseline anywhere in the decision.

**What you'll notice.**

- Every pick table is ranked by pick value, and each row shows **Now**, measured against the player
  the pick recommends: `TAKE` on his row, a signed number on everyone else, and `level` where the
  simulation genuinely cannot separate them. Exactly one `TAKE` per table, and it is the top row —
  so the table can never contradict the sentence above it.
- The plan is a real path with a Plan B and, where it matters, an "if he falls" upside line. A plan
  target has to be someone you can actually expect to be there — the floor is 50% — so a stud who
  falls to you one draft in five is now labelled as upside instead of being sold to you as a plan.
- The position heatmap is gone, replaced by **cost of waiting**: what one more turn costs you at each
  position. Both halves of that subtraction carry the same replacement level, so it cancels. Measured:
  overriding the RB replacement rank by ±20 (moving the baseline from 164 points to 92 and to 229)
  moves the RB cost-of-waiting cells by at most 4 points, while it moves the surplus levels they are
  built from by up to 73.
- The keeper verdict leads with full-draft lineup totals per scenario with standard errors
  (`--keeper-scenarios`), so it is in the same units as everything else. The isolated surplus table
  stays underneath as the explanation.
- Replacement level and surplus moved to the appendix and the tier boards, where surplus is now
  labelled **vs. free**. They still explain which pools are deep. They no longer rank anything.
- Every number carries a standard error, and the analysis says "close" when scenarios or candidates
  are within two of them.

**Runtime.** A full run on the 12-team sample league — 1,500 availability drafts, then 200 rollouts
for up to 8 candidates at each of 8 picks, plus five keeper scenarios — takes about 5–6 minutes.
`--rollouts 60` gives a rough answer in under two. `--no-pick-values` restores the fast v1 path, and
the board still renders from that output (the pick tables fall back to the surplus ranking).

**New flags.** `--pick-values` / `--no-pick-values`, `--rollouts`, `--candidates`, `--through-round`,
`--plan-min-avail`, `--keeper-scenarios`, `--watch`, `--strict`.

**New `sim.json` keys.** `pick_values`, `plan_path`, `cost_of_waiting`, `keeper_scenarios`,
`plan_check`, `rollout_settings`. Every v1 key is still written, so an older board still renders.

**Three places the build departed from the spec, and why.**

1. *A matched control arm was added to the rollouts.* The spec defines a candidate's pick value as the
   plain average over the samples where he was available. That is biased: a player who falls to you one
   time in five only falls in the drafts where the whole board fell, so he gets credit for luck that had
   nothing to do with him — in testing this put Jahmyr Gibbs (available at pick 5 in 21% of drafts) at
   the top of the pick-5 table. Each sample is now also played out with nobody forced in, and a
   candidate is scored on the *difference* he makes on his own samples. The luck sits in both terms and
   cancels. The reported number is that difference added back to the control mean, so it still reads as
   a projected lineup, and the standard errors are the paired ones — much tighter, which is the point.
2. *A plan target must be available at least 50% of the time.* Greedy-by-value alone would have made
   the plan "take Bijan at pick 5", which is not a plan when he's there one draft in five. The best
   candidate below the floor is reported as the row's upside instead. `--plan-min-avail` changes it.
3. *A failed plan check warns rather than aborts.* US-4 calls a plan that doesn't fill a legal starting
   lineup a build failure. Killing the run would also destroy the JSON the user needs, so `plan_check`
   is written to `sim.json`, printed loudly in the console summary and on stderr, and `--strict` makes
   it exit non-zero for anyone scripting it. The check itself was narrowed to the players who actually
   fill a starting slot: a round-9 receiver projecting below replacement is a bench body, not a bug.

**Two things a fresh-context test run caught, worth knowing before you read a number.**

*Pick values are comparable within a pick, not across picks.* Each pick's values are measured against
that pick's own control arm — the same drafts played out with nobody forced in — and that control
already assumes you followed the plan to get there. So the plan's projected-lineup column drifts
downward as the draft goes on. 1,858 at pick 5 and 1,842 at pick 101 are two different baselines, not
a team getting worse. `control` and `vs_control` are in the output so the drift is visible. Keeper
scenario totals come from a free-running policy and sit on a third scale again; never subtract one
from a pick value.

*Following the plan simulates to 1,839 on the sample league; letting the same simulated drafter
choose freshly at every pick gives 1,863.* The tool's own recommendation trails its own default
policy by 24 points — a point and a half a week — and that is stated in `methodology.md` §2 rather
than buried. Part of it is the price of having a plan at all (a ranking computed before the draft
can't react to the board). Part of it is a real bias worth fixing: the rest-of-draft policy inside a
rollout is the same heuristic, so forcing in a player it would not have chosen leaves it repairing a
roster shape it did not plan, and the candidate is charged for that rigidity as well as for himself.
**This is the top item for v2.1.** What survives it is the ranking and the gaps within a pick, which
is all the board asks you to read.

Two more the same run exposed once Plan B was fixed: the plan could name the same player as the
target at two different picks (the availability numbers come from a pass that doesn't know your plan
already took him), and it could plan a second quarterback in a one-QB league. Players the plan
already holds are now excluded from later candidate lists, and the plan's positional cap is what
actually starts rather than what a roster can hold.

Four smaller things the same test run found, now fixed: Plan B was chosen from the players clearing
the 50% availability floor, which could name a fallback 22 points worse than an obvious one sitting
right above it; a candidate measured on under 25 drafts could anchor the "Now" column for every other
row; kickers and defenses were missing from the availability tables in the round people actually
start taking them; and `cost_of_waiting` was computed one round deeper than the board renders it.

**Three scope claims that didn't hold, now fixed.** `draft_type: linear` was documented in
`league.example.yaml` and read nowhere — the pick ladder was hard-coded snake, so a linear-draft user
got silently wrong pick numbers and every number downstream of them. Linear is now implemented and
tested. `draft_type: auction` stops with a pointer to the methodology's dollar conversion instead of
quietly simulating a snake draft. And `scoring.te_premium` is applied by `scoring.py` when it builds
the projections, not by the simulator — setting it in `league.yaml` alongside your own `players.csv`
did nothing, silently; it now says so. (Worth knowing even when it is wired up correctly: points and
receptions scale together at tight end, so a per-reception premium lifts the whole pool nearly
proportionally. At a realistic +0.5 it did not move the first tight end in the plan on the sample
pool; at +1.5 it moved from the seventh pick to the second and tight ends began taking flex slots.
The mechanism works; the effect is smaller than intuition suggests.)

**Known and not fixed.** The simulated drafter cannot take a kicker or defense before the last two
rounds, so it will not endorse an early-round kicker even when the surplus math says one is worth it.
The written advice can therefore run ahead of what the sample drafts show. Left as is for 2.0.

**Availability changed meaning, slightly and deliberately.** "Here" and "Next" are now measured on a
pass where your own seat drafts off ADP like everyone else. Whether a player lasts to your next pick
has to be a fact about the other managers; measuring it on a pass where your plan already took him
reported every one of your own targets as 0%.
