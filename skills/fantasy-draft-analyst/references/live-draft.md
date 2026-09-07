# Local live draft workflow

Use this mode when the user needs recommendations to change after actual picks. The preparation HTML from `build_board.py` is a separate, frozen artifact. The live board needs a running Python process on the user's machine; a cloud chat's downloaded HTML cannot run that process by itself.

## Start and resume

From the installed skill directory (Python 3.10+, PyYAML for YAML league files):

```bash
python3 scripts/live_draft.py --session /path/to/output/session.json init --league /path/to/league.yaml --players /path/to/players.csv
python3 scripts/live_draft.py --session /path/to/output/session.json serve --port 8768
```

Open `http://127.0.0.1:8768`. The server accepts local same-origin requests and records manual picks; it does not connect to or submit picks on a fantasy platform. A browser on another device cannot reach this loopback address. Resume with `serve` on the same session path; `init` refuses to replace an existing session.

The page shows the current pick, state/data revisions, evidence limitations and a deterministic shortlist from the shared draft policy. Every accepted pick updates the session before recalculation. A stale state token rejects an action until the page refreshes. Never represent cached recommendations for an older pick as current advice.

## CLI and import

```bash
python3 scripts/live_draft.py --session /path/to/session.json pick "Player Name"
python3 scripts/live_draft.py --session /path/to/session.json import-picks /path/to/picks.csv
python3 scripts/live_draft.py --session /path/to/session.json undo
python3 scripts/live_draft.py --session /path/to/session.json recommend
python3 scripts/live_draft.py --session /path/to/session.json refresh --players /path/to/refreshed-players.csv
python3 scripts/live_draft.py --session /path/to/session.json export
```

Use `--help` on subcommands for exact supported options. Pick imports accept CSV or JSON rows with `pick` and `player_id`, `name` or `player`. Original pick numbers are authoritative. Keepers come from confirmed league declarations; they are removed and assigned to their owners from the start, with the charged future pick reserved.

Unknown names remain explicit placeholders occupying their original pick; resolve them with `resolve PICK PLAYER` or the live UI rather than invent a position. Unresolved own players limit numerical roster advice. Duplicate imports are idempotent; conflicting picks are errors. Corrections should rebuild from event history, not edit arrays by hand.

## Evidence and receipts

Keep the `.evidence.json` sidecar from data preparation beside the player CSV. Legacy input cannot establish source freshness and is labeled accordingly. Updating player data changes its revision while preserving pick history and earlier evidence. Each recorded choice can retain its recommendation packet, alternatives and assumptions for later review.

The deterministic explanation uses only its supplied fields. Any optional external AI explanation must pass the available-player/evidence validator; otherwise display the deterministic fallback. A well-written story is not new factual evidence.

## Draft-clock behavior

The live shortlist uses cached inputs and the shared fast decision policy. It is not the full pre-draft continuation search and its urgency label is not a calibrated live survival probability. Inspect the method and assumptions returned in the packet before explaining differences. Run deeper comparisons between picks when feasible; source fetching and remote model calls do not belong on the immediate pick path.

## Privacy and boundaries

Store sessions outside public examples and the installed skill. Session exports contain league and draft information. The local server serves only its board and fixed JSON endpoints, with no arbitrary file browsing. Exporting a session is separate from sharing it. Unsupported draft formats and ambiguous keeper costs require corrected inputs or explicitly limited analysis.

A JSON player-pool upload is a flattened list (or a `players` wrapper) with `player_id`, `name`, `pos`, `adp` and optional `proj`; it is not the raw stat-evidence snapshot. Prepare raw evidence into CSV plus sidecar first. Missing projections permit explicitly rank-only JSON advice. Unknown own-roster slots suppress numerical comparisons until resolved.

The conditional comparison samples paired opponent continuations through the actual next pick using confirmed rival rosters. Its trial count and sampling error are exposed. Eight illustrative scenarios are a fast sensitivity check, not a precise survival estimate or full-draft optimization.
