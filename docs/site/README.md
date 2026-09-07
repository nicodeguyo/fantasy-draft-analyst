# The v3 walkthrough

The public website demonstrates two **saved outputs from the shipped v3 engine**. Switching stages displays these results; the website does not execute the Python engine, access a league account, or generate personal advice.

## Inputs and source dates

- Fictional league: [The Open Draft League](../../examples/v3-live/league.json), 12 teams, half-PPR, snake, pick 5, no keepers. The roster requires QB, two RB, two WR, TE, FLEX, K, DEF, and six bench spots.
- Public input snapshot: [evidence.json](../../examples/v3-live/evidence.json), season 2026, fetched September 7, 2026 around 04:00 UTC (September 6 around 11 p.m. Central).
- Sources: [ESPN public projection API](https://lm-api-reads.fantasy.espn.com/apis/v3/games/ffl/seasons/2026/segments/0/leaguedefaults/3?view=kona_player_info), [CBS projection tables](https://www.cbssports.com/fantasy/football/stats/RB/2026/season/projections/nonppr/), and [FantasyPros projection tables](https://www.fantasypros.com/nfl/projections/rb.php?week=draft&scoring=HALF&year=2026). Each saved projection retains its own URL, stat line, fetch time, and assumptions. Vendor fantasy-point totals are not used; stat lines are rescored for the example league.
- No private league, actual user picks, news events, usage inputs, or betting inputs are included. NFL players and their public data are real; the draft is constructed.

**Limited evidence:** source update times are unverified, some scoring fields use declared zero approximations, and coverage is incomplete. FantasyPros constituents are unknown and cannot be counted as verified independent forecasts. Unmatched provider rows are absent from the normalized snapshot; incomplete player identities remain visible to the engine. No claim of complete provider coverage is made.

The snapshot is deliberately frozen. Do not use it as fresh advice for a future draft. The source pages may change without changing these saved results.

## How the example is selected

The first 18 selections follow ascending ADP among players with eligible projections and prices. At pick 19, the fictional opponent deliberately takes the preview's top candidate. This illustrates a lost target; it is not a claim about typical opponent behavior. No search for the largest favorable difference is performed.

The engine calls its normal `recommend()` function before and after the recorded pick. At pick 20, it compares Walker, Rice, and Olave, including their evidence, roster contributions, next-turn possibilities, and projection sensitivity. The current roster contains Jonathan Taylor. Confirmed keepers are supported by the product but this example has none.

The shipped recommendation packet includes eight quick paired opponent continuations to pick 29. The marketing explanation uses a separate expanded run of 800 continuations per path, preserved in [next-turn-800.json](../../examples/v3-benchmark/next-turn-800.json). They are illustrative scenarios, not calibrated availability probabilities or a full-season backtest. Roster utility is a decision score; its components are not additional points over another candidate. Source dispersion measures disagreement, not football outcome variance. Missing expected-games values and bench coverage use the engine's declared defaults; no performance-upside inputs are supplied here.

## Reproduce

From the repository root, with Python 3.10+ and PyYAML:

```bash
python scripts/build_v3_demo.py
```

The script rescoring step uses the frozen `as_of` time, then reproduces both states through the same CSV loader and policy as local live mode. It writes [v3-demo.json](v3-demo.json), including input hashes, and refreshes the marked HTML section on the homepage. It does not modify the draft engine. The public JSON omits ephemeral session tokens but preserves the evidence and scenarios behind the candidates.

To regenerate the GIF, screenshot, social preview, and narrated video, see [media reproduction](../media/README.md).

## Website behavior and accessibility

Both states are ordinary HTML; the after-pick state remains readable without JavaScript. Stage buttons have pressed states and a status announcement. Source details use native disclosure controls. No automatic animation is necessary to understand the example. The site retains the navy/lime design, requires no remote fonts, and contains no analytics or account access. The starter-prompt copy button has a text-selection fallback.

Preview from the repository root:

```bash
python3 -m http.server 8765 --bind 127.0.0.1
```

Open `http://127.0.0.1:8765/`. GitHub Pages deploys `main`, root. Relative assets work under the project path `/fantasy-draft-analyst/`.

## Historical assets

The [v2 site](../archive/v2-site.html), [benchmark](../archive/v2-benchmark.md), saved preparation board, and original media are archived. `build_demo.py` and `build_launch_evidence.py` now target the archive, so reproducing historical evidence cannot overwrite the current homepage. The current homepage does not use the archived performance claim.

## Current benchmark and marketing proof

The three-row marketing table is backed by [800-room results](../../examples/v3-benchmark/README.md): +66.226 projected starter points versus disciplined ADP and +104.307 versus the noisy bot, rounded to +66 and +104. V3 had the stronger projected lineup in 793 of 800 rooms. The complete research retains the legacy comparison; it is not included in the marketing table.

The Walker explanation uses 11/800 = 1.375% (shown as 1.4%), 247/800 = 30.875% (shown as 30.9%), and 7.457 points (shown as 7.5). Each probability is conditional on the choice described beside it. Sources, modeling assumptions, and complete results remain in the linked research; shared qualifications are not repeated on each candidate card.
