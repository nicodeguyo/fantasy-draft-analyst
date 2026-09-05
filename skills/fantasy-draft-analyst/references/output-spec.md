# Output spec — the exact shape of the analysis and the board

The user should be able to read the analysis top to bottom on a phone and know what to do at every pick. Use the section order below. Templates show the level of specificity expected; the numbers are illustrative.

Contents

1. The written analysis (sections 1–9)
2. The appendix
3. `notes.json` schema for the draft-day board
4. The board itself
5. Style rules

---

## 1. The written analysis

### 1. Keeper verdict (keeper leagues only)

```
## Verdict: keep <Player>

<One sentence on why it isn't close, or why it is.>

### The verdict in lineup points
Full drafts simulated under each scenario (`keeper_scenarios`):

| Scenario | Cost | Projected starting lineup | SE |
|---|---|---|---|
| Keep <A> | R6 | 1,864 | ±0.6 |
| Keep <B> | R3 | 1,824 | ±0.8 |
| Keep nobody | — | 1,810 | ±0.9 |

<Compare small scenario gaps with their uncertainty, without treating marginal SEs as a paired test. Break the
tie on the bear case, not the decimal.>

### The keeper math
Your picks at slot <s> in a <T>-team snake: <ladder>.

| Player | Cost | You pay (pick) | ADP | Surplus (picks) | Surplus (points) |
|---|---|---|---|---|---|
| ... |

### Why <Player>, beyond the number
- Keeper inflation: <K> players come off the board before anyone picks... <what pick p really buys>
- Points-per-pick is steepest at the top...
- The player himself: <2025 line, role, health, contract, target competition> (source, date)
- The honest bear case: <...>

### The one thing you must confirm first
<The eligibility/rule question that could flip this, and what the answer changes.>

### Why not the tempting alternatives
<Each candidate in one paragraph, with the number.>

### What you sacrifice by keeping nobody
<Who you'd lose that you can't re-draft at the same price.>
```

### 2. How the picks were valued

```
## How every number on this page was produced
For each of your picks, each candidate was planted at that pick and the rest of the draft was
simulated <R> times — the room drafting off ADP, you drafting sensibly afterwards — and the
resulting starting lineup scored. **Pick value** is that projected lineup. The player with the
highest one is the pick; the gap below him is what the alternative costs you.

Replacement level, for context rather than for decisions:

| Pos | Replacement | Who that is |
|---|---|---|
| QB | 312 | QB12 |
| RB | 164 | RB28 |
| WR | 156 | WR35 |
| TE | 116 | TE13 |

<One sentence on what the RB/WR gap says about which pool is deeper — and one on why that number
is an explanation and not the ranking: move it three ranks and every back gains twenty points of
surplus, which is exactly why the pick tables are simulated instead.>
```

### 3. Pick geometry and the cost of waiting

Ladder with keeper-forfeited rounds removed; turn structure; the measured inflation at your early picks. Then the cost of waiting:

```
### What waiting costs at each of your picks
Points of value lost by waiting until your next turn (from `cost_of_waiting`):

| Pick | QB | RB | WR | TE |
|---|---|---|---|---|
| 5 | 7 | **47** | 38 | 5 |
| 20 | 2 | 6 | 11 | **22** |
| ... |

Reading: <two sentences — which position is about to run out at each turn, and where the columns
go flat so a position can wait. Then the plan that follows from it.> This table is unaffected by
where replacement level is drawn in the direct subtraction: the same constant cancels, though changed assumptions can still alter simulated draft paths.
```

### 4. The board — top five at each pick

For each pick:

```
### Pick 20 (R2) — <decision sentence>
| Player | Pos | Proj | Pick value | Now | Here | At 29 |
|---|---|---|---|---|---|---|
| Drake London | WR | 215 | 1,861 | TAKE | 62% | 1% |
| Brock Bowers | TE | 192 | 1,861 | close | 50% | 8% |
| Trey McBride | TE | 188 | 1,856 | −5 | 71% | 20% |
| ... five rows ...
<One sentence naming an alternative and explaining the tradeoff. “Close” means an absolute projected gap below one point, a rounding convention. Explain small gaps without claiming statistical equivalence.>
```

Pick values support model-based comparisons **within** a pick, with potentially different candidate availability populations, and not across picks (each is measured against that pick's own control arm, which assumes you followed the plan to get there) and not against a keeper-scenario total. Say so once in §2 rather than letting a reader subtract one from another.

"Now" is `row.value − plan_path[pick].value` — the gap against the player the pick actually recommends, **not** against `delta_vs_best`, which is measured from the highest raw value and can sit on a player who reaches you one draft in five. Use the same subtraction in the analysis as the board does, or the two will disagree at exactly the picks where it matters. It reads: `TAKE` on his row, a positive number on anyone worth more if he happened to fall to you, a negative number on anyone worth less, and `close` for an absolute gap below one projected point (a rounding convention, not a statistical test). There is exactly one `TAKE` per table and it is the top row, so the table can never disagree with the decision sentence above it. “Here” / “At [pick]” are availability at that pick and at the following one, measured across the simulations with your own seat drafting off ADP as unconditional pre-draft frequencies. They are not survival probabilities after deliberately passing on a player who is available now. Label the simulated or analytical method used.

### 5. Tiers with cliffs

Per position: tier label, players with team/ADP/projection, and a cliff line between tiers with the point drop and a one-sentence meaning ("−25: the largest gap on the board. Pay here or skip to tier 2 and pocket four rounds."). Mark the user's owned/targeted players.

### 6. Your guys, pressure-tested

Per player, the five-part template from `references/metrics.md` §6, ending with a verdict tag: TAKE at <pick> / OK at <pick>+ / NOT BEFORE <pick> / PASS / FADE. Then "Two names to add" and the reach rule applied to their actual picks.

### 7. Sample drafts and the target build

Range of projected totals; most-owned players; "what happened in every draft". Then the target build, which is `plan_path` — one row per pick with the target, the projected lineup, how often he's actually there, the Plan B and what it costs, and the "if he falls" upside:

```
| Pick | Target | Projected lineup | There | If he's gone | If he falls |
|---|---|---|---|---|---|
| 5 | Jaxon Smith-Njigba | 1,858 | 63% | Jonathan Taylor (−22) | Bijan Robinson (21%) |
| 20 | Brock Bowers | 1,859 | 50% | Drake London (close) | — |
```

Then why this one, the honest weakness, and the hedge. If `plan_check` did not pass, say so and fix the plan before publishing it.

### 8. The late-round plan

Handcuffs to own, second-year upside, next-year keeper logic, K/DEF timing.

### 9. Assumptions worth checking before you commit

Bullet list: eligibility, league size, superflex, escalation, and the one assumption that flips the board.

## 2. The appendix

- **Terms** — from `references/glossary.md`, only the ones used.
- **Scoring applied** — the full formula.
- **Sources and dates** — ADP source and window, projection source and update date, news sources and fetch date, betting source and date.
- **Projections I changed from consensus** — three to five players, the change, the reason.
- **Simulation settings** — runs, keeper model, opponent model, replacement ranks, the measured inflation at your picks, and the note that keeper surplus is measured against a keeper-free probe (slightly conservative — the real alternative at that pick is a little worse once other teams' keepers are gone).
- **Assumptions** — lineup assumed, injury handling, K/DEF treatment.

## 3. `notes.json` schema for the board

`scripts/build_board.py` merges the simulator output with this file. Everything in it is prose you wrote; keep each string short enough to read at a glance.

```json
{
  "title": "Replacement Level",
  "subtitle": "2026 draft board · pick 5 of 12 · ESPN",
  "chips": ["Half PPR · 0.5 per catch", "4-pt passing TD · −2 INT", "1 flex", "Keeping Chase Brown (R6 · pick 68)"],
  "howto": null,
  "plan_sub": "Your target at every pick, with the fallback if he's gone.",
  "plan": [
    {"pick": "KEEP", "player": "Chase Brown", "alt": ""},
    {"pick": "5", "player": "Jaxon Smith-Njigba", "alt": "Jonathan Taylor (−22); Bijan Robinson if he falls (21%)", "note": "WR1 — the tier ends here"},
    {"pick": "20", "player": "Brock Bowers", "alt": "Drake London — close projected gap"}
  ],
  "plan_total": "1,856 projected starting lineup",
  "target_note": "Across ten simulated drafts the range was 1,772 to 1,906...",
  "waiting_note": "Waiting on a back costs 47 points at pick 5 and almost nothing after 44; tight end has windows at 20 and 53; quarterback never costs more than six until round 5, so it waits.",
  "headline_rule": {
    "heading": "What replacement level tells you, and what it doesn't",
    "paragraphs": [
      "In a 12-team league with one flex, the 28th running back and the 35th receiver are the worst players anyone has to start...",
      "That gap is why the receiver pool is the deeper one. It is not what ranks your picks — move it three ranks and every back gains twenty points of surplus, which is exactly why the tables above are simulated instead..."
    ]
  },
  "pick_notes": {
    "5": {"note": "Running back if Bijan fell (21%). Otherwise Jaxon Smith-Njigba.", "plan_b": "Jonathan Taylor (52%), then James Cook III (76%)"},
    "20": "Tight end. Bowers if he's there (52%); McBride if not (72%). The 25-point cliff below them closes before 29."
  },
  "late_note": "Nothing back here moves your lineup. Kicker and defense in the final two rounds only.",
  "late_body": "Spend rounds 9 through 13 on two things...",
  "tiers": {
    "RB": {
      "subtitle": "replacement 164 · 28 get started weekly",
      "bands": [
        {"label": "Tier 1", "note": "win the league by themselves", "players": ["Jahmyr Gibbs", "Bijan Robinson"]},
        {"cliff": "−41", "cliff_note": "Both are kept in almost every league. Assume they're gone."},
        {"label": "Tier 2", "note": "true first-rounders", "players": ["Jonathan Taylor", "..."]}
      ]
    }
  },
  "mine": ["Chase Brown", "Brock Bowers", "Bucky Irving"],
  "shortlist": [
    {"player": "Bucky Irving", "call": "TAKE AT 44", "tag": "take"},
    {"player": "Jaylen Waddle", "call": "PASS AT 44 · OK AT 53", "tag": "pass"},
    {"player": "Kyle Pitts Sr.", "call": "OK AT 53 IF NO TE", "tag": "ok"}
  ],
  "vegas": [
    {"value": "10.5", "text": "Bengals win total, under −120. A mild negative for a back whose value came partly from shootouts."}
  ],
  "appendix": {
    "terms": [{"term": "Replacement level", "def": "The score of the worst player at a position who still has to be in someone's starting lineup every week."}],
    "how_built": ["Projections are mine, not a vendor's...", "ADP source: ...", "Simulation: ..."],
    "assumptions": ["Starting lineup assumed: ...", "Kickers and defenses are treated as near-interchangeable..."],
    "flip_warning": "The one assumption that could flip this whole board: ...",
    "gold_warning": "The simulated opponents draft rationally off ADP. Your actual leaguemates don't..."
  },
  "repo": "nicodeguyo/fantasy-draft-analyst"
}
```

Field notes:

- `plan` is the target build, one row per pick plus the keeper. It should be `sim.json`'s `plan_path` wearing your prose; omit it entirely and the renderer builds it from `plan_path` alone. Each row may carry `value` and `plan_b_value`, but you rarely need to: the renderer reads both from `plan_path` when they're absent, which is what keeps the board and the analysis from ever disagreeing. `alt` is the Plan B shown in the "If he's gone" column — name the fallback and what it costs; leave it out and the renderer writes it from `plan_path` (including the "if he falls" upside line). `note` (optional) is a short label under the name. `plan_total` (or `plan_total_label`) is a display string; if omitted the renderer uses the plan path's final projected lineup. The older `target_build` shape is still accepted.
- `shortlist_sub` overrides the one-line subtitle above the shortlist table. `waiting_note` is the two-sentence reading of the cost-of-waiting table (the renderer draws the table from `sim.json`'s `cost_of_waiting`). The old key name `roadmap_note` still works.
- `pick_notes` values may be a string or `{"note": ..., "plan_b": ...}`; the Plan B renders under the decision sentence and its players are always shown in that pick's table.
- `howto` may override the four "how to use this on draft day" steps as `[[heading, body], ...]`; leave it `null` to use the defaults, which are right for almost everyone.
- `headline_rule.paragraphs` should quote the league's actual replacement numbers and the flex fill from `sim.json`.
- Player names in `plan`, `pick_notes`, `tiers`, `mine`, and `shortlist` must match `players.csv` exactly (full names).

**Limited rich-text formatting.** `appendix.how_built`, `appendix.assumptions` and `headline_rule.paragraphs` support only `<b>`, `<strong>`, `<em>`, `<i>`, `<br>` and `<code>`. The renderer rebuilds those tags without any attributes, balances unclosed formatting tags, and displays other tags as escaped text. Comments and declarations are omitted. Links, images, scripts, embedded documents, styles and event handlers cannot be introduced through these fields. Malformed declarations fall back to plain escaped text.

User-supplied `howto` bodies and tier labels are plain text and HTML-escaped, as are player names, notes and verdicts. Values embedded in JavaScript use script-safe JSON; custom colors must be six-digit hex values (`#RRGGBB`). Simulation numeric fields are expected to come from `draft_sim.py`, not arbitrary untrusted JSON. Formatting safeguards do not verify the accuracy of someone else's notes or simulation results.

`tiers.*.bands[].players` are names that must match `players.csv`; the renderer looks up team, ADP, and projection. `mine` marks rows gold. `shortlist[].tag` is one of `take`, `ok`, `pass`. Every key is optional: a pick without a `pick_notes` entry shows "Take the top row.", and a missing `tiers`, `shortlist`, `vegas`, or `target_build` leaves that section empty, so fill them all in. `headline_rule` now lives in the appendix, where replacement level belongs. `repo` (the GitHub `owner/name` in the footer credit) may also live under `appendix`.

Renderer flags and generated policy are authoritative. `--max-pick` limits the timing heatmap, not the complete pick tables. The board's default policy shows every available draft turn, including the late rounds. Use the displayed target first, then the displayed alternatives and expanded rows. Beyond the rollout horizon, identify the shared surplus fallback clearly rather than labeling it a simulated pick value. Keep specific late targets in `notes.plan` so the benchmark and rendered board agree. Check `--help` before changing display limits, and ensure any non-default display still exposes the complete decision policy being claimed in a benchmark.

## 4. The board itself

One HTML file, no external dependencies except a Google Font, in the user's team colors. Structure, top to bottom — the order is deliberate: what to do first, the plan, the tools that keep the plan honest during the draft, then the reference material:

1. Masthead — team name, subtitle, setting chips.
2. Sticky pick ladder — PLAN first, then every pick number, then TIERS / CALLS / NOTES.
3. **How to use this on draft day** — four numbered steps: before the draft, on the clock, when someone else drafts a player (tap him), when you draft a player (tap ✓).
4. **The plan** — the target at every pick with round, the projected starting lineup it produces, how often he's there, "If he's gone", and the "if he falls" upside; the plan total; the target note.
5. **Cost of waiting** — points lost per position by waiting one more turn (QB/RB/WR/TE × your picks), the outlined cell marking the position about to run out, and the waiting sentence.
6. **Your lineup** — every starting slot, filled in as the user taps ✓; a running projected total and a bench line.
7. Your picks in order — one block per pick: decision sentence, Plan B, and the table ranked by pick value with **Now** (`TAKE` on the recommended player, signed points against him below) and **Pre-draft availability** (frequency at the following pick; not conditional live survival), plus a ✓ button per row.
8. Late rounds block.
9. Tier boards by position with cliffs (each row shows projection and "vs. free").
10. Your shortlist, scored — verdict tags; the Vegas list.
11. Appendix — terms, **replacement level and what it explains**, how the numbers were built, assumptions, the two warnings.
12. Toolbar — taken / mine counters, Hide taken, Reset, Print.

Behaviors: tap any player row to mark him taken (greys out everywhere); tap ✓ to mark him yours (gold, fills the lineup); state persists in the browser's localStorage under a key derived from the title, so a reload mid-draft keeps everything; Hide taken collapses crossed-off rows; print hides the ladder, toolbar, and ✓ buttons and breaks pages before picks, tiers, shortlist, and appendix.

## 5. Style rules

- Decision sentence per pick: position first, then the name, then the contingency. "Running back. Saquon if he fell. Otherwise Hampton."
- Pick-value tables promote the prepared target, then use the shared candidate order. Label late rounds without rollouts as surplus-based choices. The rendered table and benchmark must use the same target, alternatives, and fallback.
- Numbers as integers for projections and surplus; percentages without decimals.
- Sources and dates in the appendix, not inline, except when correcting the user's premise.
- Length: sections 1–4 and 7–9 together should read in under ten minutes (roughly 2,500 words). The pressure tests (≤200 words each), the tier boards, and the appendix are on top of that; a full one-keeper analysis with six flagged players lands around 4,000–5,000 words plus tables. Cut repetition, not sections.
