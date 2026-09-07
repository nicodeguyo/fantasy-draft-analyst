# v3 release validation

Local verification on September 6, 2026 (America/Chicago), Python 3.14.6:

- 84 behavioral/correctness tests passed, including real local HTTP requests, CLI imports, undo, stale-state handling, concurrent writer rejection, source outages, source period/scoring validation, roster coverage, projection sensitivity and held-out evaluation boundaries.
- The ZIP was built twice with identical bytes, extracted outside the repository and used to prepare synthetic evidence, initialize a live session, record a pick, recalculate and undo. No repository-relative core dependency was needed.
- Embedded live-board JavaScript passed `node --check`. Initial browser accessibility inspection confirmed the live page, roster requirements and pick controls loaded. Further native interaction was unavailable when the machine locked; HTTP interaction is covered by executable tests.
- Public provider verification at 2026-09-07 04:00 UTC yielded 464 eligible rows, with zero fetch failures. Accepted stat records: ESPN 388, CBS 345, FantasyPros 39. FantasyPros public tables exposed limited rows; one FantasyPros and 23 CBS identities were quarantined. Raw provider data is not redistributed.
- A real-feed live session retained 1,000 identities, used 464 projected players and returned three candidates in limited-projection mode. At the user's pick 9 in a synthetic 14-team league, next-turn comparisons and source sensitivity took approximately 0.16 seconds locally. This is a smoke measurement, not a latency guarantee.
- Evidence remained **limited**, correctly: source update details, public consensus independence and some statistical assumptions are incomplete. Requesting three providers does not make every player a verified three-source forecast.

The new default score is transparent roster utility. The archived 800-draft comparison does not test it. No historical win-rate or real-season superiority claim is made. The held-out evaluator covers fixed-roster one-pick decisions with pre-lock weekly forecasts; it is not a complete season/waiver counterfactual. Windows locking is implemented using its standard-library API but was not runtime-tested locally. CI adds Linux Python 3.10 and 3.12 coverage; consult the actual workflow results before claiming those passed.

Reproduce local checks with `python3 -m unittest discover -s tests -v`, `python3 scripts/package.py`, and the commands in the install/evidence/live references. Network-dependent provider availability is separate from deterministic synthetic correctness tests.

Final independent reviews caught and fixed duplicate display names rejecting canonical identities, partial feeds unnecessarily disabling all numerical advice, duplicate bye-week coverage and explicit zero defensive points allowed being treated as missing. Each has a regression test. The optional no-mistakes runner failed before its review because the installed CLI cannot run its configured model; its failure is not a passed check. Delivery uses the independent reviews, executable suite, package checks and actual [GitHub CI](https://github.com/nicodeguyo/fantasy-draft-analyst/pull/1/checks).
