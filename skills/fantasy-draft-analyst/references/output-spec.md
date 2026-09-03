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

### 2. The one number

```
## The number that drives everything
Replacement level in a <T>-team, <flex> league, in your scoring:

| Pos | Replacement | Who that is |
|---|---|---|
| QB | 312 | QB12 |
| RB | 137 | RB34 |
| WR | 165 | WR32 |
| TE | 114 | TE14 |

That <gap>-point gap between RB and WR replacement is the entire draft. <One example of a higher-projection WR being the worse pick.>
```

### 3. Pick geometry

Ladder with keeper-forfeited rounds removed; turn structure; what inflation does ("with <K> keepers gone, pick 20 delivers a true-ADP-30 player").

### 4. The board — top five at each pick

For each pick:

```
### Pick 20 (R2) — <decision sentence>
| Player | Pos | Proj | Surplus | There % |
|---|---|---|---|---|
| Brock Bowers | TE | 192 | +78 | 52% |
| ... five rows ...
<One sentence naming the sixth option and why it lost.>
```

"There %" is the availability at that pick across the simulations (or the analytical estimate — say which).

### 5. Tiers with cliffs

Per position: tier label, players with team/ADP/projection, and a cliff line between tiers with the point drop and a one-sentence meaning ("−25: the largest gap on the board. Pay here or skip to tier 2 and pocket four rounds."). Mark the user's owned/targeted players.

### 6. Your guys, pressure-tested

Per player, the five-part template from `references/metrics.md` §6, ending with a verdict tag: TAKE at <pick> / OK at <pick>+ / NOT BEFORE <pick> / PASS / FADE. Then "Two names to add" and the reach rule applied to their actual picks.

### 7. Sample drafts and the target build

Range of projected totals; most-owned players; "what happened in every draft"; the target build as a table (KEEP / pick → player → proj); why this one; the honest weakness and the hedge.

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
  "headline_rule": {
    "heading": "The only number you need to remember",
    "hot": {"value": 137, "label": "worst RB you'll ever have to start"},
    "cool": {"value": 165, "label": "worst WR you'll ever have to start"},
    "paragraphs": [
      "In a 12-team league with one flex, about 34 running backs and 32 receivers start every week...",
      "So a receiver is worth 28 points less than his raw projection suggests..."
    ]
  },
  "pick_notes": {
    "5": "Running back if Bijan fell (21%). Otherwise Jaxon Smith-Njigba.",
    "20": "Tight end. Bowers if he's there (52%); McBride if not (72%). The 25-point cliff below them closes before 29."
  },
  "late_note": "Nothing back here moves your lineup. Kicker and defense in the final two rounds only.",
  "late_body": "Spend rounds 9 through 13 on two things...",
  "tiers": {
    "RB": {
      "subtitle": "replacement 137 · 34 get started weekly",
      "bands": [
        {"label": "Tier 1", "note": "win the league by themselves", "players": ["Jahmyr Gibbs", "Bijan Robinson"]},
        {"cliff": "−41", "cliff_note": "Both are kept in almost every league. Assume they're gone."},
        {"label": "Tier 2", "note": "true first-rounders", "players": ["Jonathan Taylor", "..."]}
      ]
    }
  },
  "mine": ["Chase Brown", "Brock Bowers", "Bucky Irving"],
  "shortlist_sub": "The names you flagged, run through the same surplus math.",
  "shortlist": [
    {"player": "Bucky Irving", "call": "TAKE AT 44", "tag": "take"},
    {"player": "Jaylen Waddle", "call": "PASS AT 44 · OK AT 53", "tag": "pass"},
    {"player": "Kyle Pitts Sr.", "call": "OK AT 53 IF NO TE", "tag": "ok"}
  ],
  "vegas": [
    {"value": "10.5", "text": "Bengals win total, under −120. A mild negative for a back whose value came partly from shootouts."}
  ],
  "target_build": {
    "total": 1858,
    "rows": [{"pick": "KEEP", "player": "Chase Brown"}, {"pick": "5", "player": "Jaxon Smith-Njigba"}, {"pick": "20", "player": "Brock Bowers"}]
  },
  "target_note": "Across ten simulated drafts the range was 1,772 to 1,906...",
  "appendix": {
    "terms": [{"term": "Replacement level", "def": "The score of the worst player at a position who still has to be in someone's starting lineup every week."}],
    "how_built": ["Projections are mine, not a vendor's...", "ADP source: ...", "Simulation: ..."],
    "assumptions": ["Starting lineup assumed: ...", "Kickers and defenses are treated as near-interchangeable..."],
    "flip_warning": "The one assumption that could flip this whole board: ...",
    "gold_warning": "The simulated opponents draft rationally off ADP. Your actual leaguemates don't..."
  },
  "repo": "nicoandmelissa/fantasy-draft-analyst"
}
```

`tiers.*.bands[].players` are names that must match `players.csv`; the renderer looks up team, ADP, and projection. `mine` marks rows gold. `shortlist[].tag` is one of `take`, `ok`, `pass`. Every key is optional: a pick without a `pick_notes` entry shows "Best surplus on the board.", and a missing `tiers`, `shortlist`, `vegas`, or `target_build` leaves that section empty, so fill them all in. `headline_rule.hot`/`cool` default to the RB and WR replacement numbers from `sim.json`. `repo` (the GitHub `owner/name` in the footer credit) may also live under `appendix`.

Renderer flags worth knowing: `--top N` sets rows per pick (default 7); `--max-pick` sets the last pick that gets its own table (default: through round 9). Any player named in a `pick_notes` entry, the shortlist, or the target build is always shown in that pick's table if he was available there at all, so the decision sentence never names someone the table hides. Any pick with a `pick_notes` entry is rendered even past `--max-pick`.

## 4. The board itself

One HTML file, no external dependencies except a Google Font, in the user's team colors. Structure, top to bottom:

1. Masthead — team name, subtitle, setting chips.
2. Sticky pick ladder — tap a pick number to jump to that turn.
3. The one rule — replacement numbers and the two-paragraph explanation.
4. How to read it — Proj / Surplus / There / Tap.
5. Your picks in order — one block per pick with the decision sentence and the surplus-ranked table with There % bars.
6. Late rounds block.
7. Tier boards by position with cliffs.
8. Your shortlist, scored — verdict tags; the Vegas list; the target build.
9. Appendix — terms, how the numbers were built, assumptions, the two warnings.
10. Toolbar — crossed-off counter, Reset, Print.

Behaviors: tap any player row to cross him off everywhere; print hides the ladder and toolbar and breaks pages before tiers, shortlist, and appendix.

## 5. Style rules

- Decision sentence per pick: position first, then the name, then the contingency. "Running back. Saquon if he fell. Otherwise Hampton."
- Every table sorted by surplus, never by projection.
- Numbers as integers for projections and surplus; percentages without decimals.
- Sources and dates in the appendix, not inline, except when correcting the user's premise.
- Length: sections 1–4 and 7–9 together should read in under ten minutes (roughly 2,500 words). The pressure tests (≤200 words each), the tier boards, and the appendix are on top of that; a full one-keeper analysis with six flagged players lands around 4,000–5,000 words plus tables. Cut repetition, not sections.
