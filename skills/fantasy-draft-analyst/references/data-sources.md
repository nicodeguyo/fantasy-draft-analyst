# Data sources — verified, by platform, with a fetch order

Every URL here was fetched successfully without a login as of September 2026. Sites change; if one fails, move to the next in the list and say which you used. Always record the date shown on the page (or the fetch date if none is shown) in the appendix.

Contents

1. Freshness rules
2. Platform-specific ADP (the most important input)
3. Consensus projections with stat lines
4. Injury and depth-chart news
5. Betting market
6. Usage and advanced stats
7. Platform quirks (why platform ADP matters)
8. The `players.csv` format the scripts expect

---

## 1. Freshness rules

- ADP older than 7 days is stale in the last two weeks before Week 1; older than 3 days is stale in draft week. Say the date.
- Re-check injury news for every player in the board, tiers, and the user's list within 72 hours of the draft. A player who missed Wednesday practice in draft week is a different pick.
- Projections: consensus pages update daily in late August/September. Use the "last updated" stamp.
- Prefer sources that print a date. If none does, state the fetch date.
- If the user's draft is more than a week away, tell them to re-run the board the day before.

## 2. Platform-specific ADP

Drafters follow their platform's default rankings, so the ADP that matters is the one from the site the league is hosted on.

| Platform | Source (verified) | Notes |
|---|---|---|
| **Any platform, cross-platform table** | `https://www.footballguys.com/adp?season=2026&pos=all` (also `pos=qb/rb/wr/te`) | One server-rendered table with overall pick numbers per platform: Consensus, ESPN, Yahoo, Sleeper (1QB / Redraft / Superflex), CBS, FFPC, NFFC, Underdog, DraftKings, MFL, RTSports. **Best first stop for Yahoo, FFPC, NFFC, MFL.** |
| **ESPN** | **First choice from a chat/fetch tool: the Footballguys ESPN column above.** From a shell with network: `https://lm-api-reads.fantasy.espn.com/apis/v3/games/ffl/seasons/2026/segments/0/leaguedefaults/3?view=kona_player_info` with header `X-Fantasy-Filter: {"players":{"limit":300,"sortDraftRanks":{"sortPriority":100,"sortAsc":true,"value":"PPR"}}}` (`scripts/fetch_adp.py --source espn` does this) | JSON with `ownership.averageDraftPosition`, ESPN's default ranks (`draftRanksByRankType`), `injuryStatus`, and ESPN season projections. Without the header it returns players alphabetically, which makes it useless from a text fetcher that can't send headers. Position ids: 1 QB, 2 RB, 3 WR, 4 TE, 5 K, 16 DST. |
| **Yahoo** | Footballguys "Yahoo!" column | Yahoo's own draft-analysis page is JavaScript-only. Yahoo ADP is based on standard scoring. |
| **Sleeper** | Footballguys "Sleeper Redraft / 1QB / SF" columns; `https://www.stackedfantasy.com/exploit-adp/sleeper` for Sleeper ADP-vs-rank gaps; `https://api.sleeper.app/v1/players/nfl/trending/add?lookback_hours=24&limit=25` for momentum | No official Sleeper ADP endpoint. Trending returns player ids; resolve with the Sleeper players dump (`https://api.sleeper.app/v1/players/nfl`, ~5 MB, cache it once per day). |
| **CBS** | `https://www.cbssports.com/fantasy/football/draft/averages/` | Server-rendered: rank, player, trend, average position, hi/lo, percent drafted. |
| **Underdog (best ball)** | `https://www.bestballteambuilder.com/underdog-best-ball-average-draft-position` | Dated table with Underdog ADP, round/overall, 3/5/9-day deltas, projected points. |
| **FFPC / NFFC / MFL / DraftKings / RTSports** | Footballguys columns | No public first-party page loads without login. |
| **Format-matched mock ADP (any host)** | `https://fantasyfootballcalculator.com/adp/{ppr|half-ppr|2qb|dynasty|rookie}/{8|10|12|14}-team/all` (standard: `/adp/12-team/all`) | Server-rendered with std dev, high, low, and draft count. Mock-draft based (more autopicks, less discipline than real leagues). Gives `adp_sd`, which the simulator uses. The JSON/CSV API is disallowed to automated fetchers by robots.txt; use the HTML page or `scripts/fetch_adp.py --source ffc` from your own machine. |
| **Consensus/expert ADP with injury column** | `https://www.rotowire.com/football/adp.php` | Dated; platform columns sometimes empty. |

Combine: use platform ADP as the price, FFC's std dev as the spread. If the platform has no spread data, use `max(4, 0.08 × ADP)` as the standard deviation. `scripts/merge_adp.py --players players.csv --adp adp_platform.csv` overwrites `adp` for every matched name and keeps the spread; players the platform file doesn't cover keep their mock ADP (say so in the appendix — There % past that depth mixes two sources).

## 3. Consensus projections with stat lines

- `https://www.fantasypros.com/nfl/projections/{qb|rb|wr|te|k|dst}.php?week=draft&scoring={STD|HALF|PPR}` — consensus season stat lines (attempts, yards, TDs, receptions, fumbles) with a "last updated" date. Six pages; space requests about a minute apart to avoid rate limiting. Re-score the stat lines in the league's system with `scripts/scoring.py`; the FPTS column is only right if the scoring matches.
- ESPN's own projections come with the ESPN API above (`stats` entries with `statSourceId 1` for the 2026 season).
- Underdog's projected points are on the bestballteambuilder table (half-PPR).

## 4. Injury and depth-chart news

- `https://fantasyfootballcalculator.com/players/<first-last>/news` (e.g. `/players/bhayshul-tuten/news`) — dated news items for one player, with last season's stat line and role notes. The best free per-player news page found in testing; slugs occasionally differ (`kyle-pitts` vs `kyle-pitts-sr`), so search the site if one 404s.
- `https://www.fantasypros.com/nfl/injury-news.php` — timestamped practice reports and injury blurbs (long page; a fetch tool may only surface the first screen).
- `https://www.rotowire.com/football/news.php` — dated player-news feed with role notes ("part of RB mix with…").
- `https://api.sleeper.app/v1/players/nfl/trending/{add|drop}?lookback_hours=24` — what thousands of managers are adding/dropping right now; a fast read on hype and injury reaction.
- `https://api.sleeper.app/v1/players/nfl` — per-player `injury_status`, `depth_chart_order`, `age`, `years_exp`.
- Team beat reporters via web search for a specific player: search `"<player name>" practice` limited to the last 3 days. ESPN.com stories render with JavaScript and come back empty to text fetchers — use the Yahoo, NBC, or CBS mirror of the same report.

## 5. Betting market

- `https://www.vegasinsider.com/nfl/odds/win-totals/` — dated win totals with over/under prices across several books. Note the juice.
- `https://www.vegasinsider.com/nfl/odds/futures/` — awards and futures.
- Season-long player props: no single free table loads reliably, and sportsbook/RotoWire odds pages load their lines with JavaScript. Search `"<player>" receiving yards prop 2026` or `season long props` and cite the article and date; RotoWire's props page and Sharp Football's season-long props articles carry a handful of lines each.

## 6. Usage and advanced stats

- `https://www.pro-football-reference.com/years/2025/receiving_advanced.htm` and `rushing_advanced.htm` — last season's targets, air yards (aDOT), yards before/after catch, drops, broken tackles. Free, but last season only, and no route/snap share.
- `https://www.playerprofiler.com/nfl/<player-slug>/` — free: air yards, targets, opportunity metrics, workout metrics, Underdog ADP. Route share, target share, and YPRR are behind a paywall.
- Route share / snap share / TPRR for the current preseason are mostly paywalled (PFF, FantasyPoints, Next Gen Stats). Use web search for `"<player>" route share` restricted to the last two weeks; analysts quote the numbers in free articles. Always note the sample size.
- Team pace and pass rate: search `pass rate over expectation 2026` for the current preseason article set.

## 7. Platform quirks

Why platform ADP matters — with the recurring patterns (verify against this year's Footballguys table):

- **ESPN**: ADP is from real ESPN drafts and tracks ESPN's default ranks closely; where ESPN's rank and the market disagree, the room follows ESPN. Elite QBs and TEs go earlier than mocks (Josh Allen ~17 on ESPN vs ~38 on Underdog in 2026), receivers on new teams and post-hype receivers slide 8–10 picks, and ESPN's default 2-WR lineup depresses mid-round WRs. Exploit: the ESPN rank/ADP gaps, and the WR band that ESPN rooms undervalue.
- **Yahoo**: sharp default ranks, so ADP ≈ Yahoo rank. QB1s go 5–8 picks earlier than on Underdog; WRs pushed down; TEs historically undervalued by an older user base. Yahoo ADP is computed on standard scoring even for PPR leagues.
- **Sleeper**: younger, Zero-RB-leaning users; RBs slide, receivers and elite TEs rise; the QB market is a barbell — the top two or three QBs go very early, everyone else very late (mid-tier veteran QBs are the best value on Sleeper). Separate 1QB, redraft, and superflex ADPs exist; use the right one.
- **CBS**: stronger RB lean than mocks.
- **Underdog**: best-ball, 18-man rosters, no waivers — depth backs, handcuffs, rookies, and late-round upside are drafted earlier and ADP is meaningful to pick ~216; camp hype moves it within days. QBs go later than on ESPN/Yahoo.
- **FFPC**: TE-premium scoring (1.5 PPR for TEs) is the FFPC standard in most formats; QBs go much later than on ESPN.
- **FFC (mocks)**: explicitly mock-draft based, which means more autopicks and less roster discipline than real leagues; treat it as the format baseline and the source of spread, not as the price.

In each case the exploit is the same: find where the platform's room is systematically early or late relative to your surplus ranking, and let them overpay for the early stuff while you buy the late stuff.

## 8. The `players.csv` format

Every script reads this file:

```
name,pos,team,adp,adp_sd,proj,bye,note
Jahmyr Gibbs,RB,DET,1.5,0.7,288,6,
Bhayshul Tuten,RB,JAX,53.0,6.5,200,8,co-starter per Coen; Rodriguez foot surgery
```

- `adp` — overall pick number on the user's platform (or the format-matched mock ADP with a note).
- `adp_sd` — spread of that ADP. Leave it blank if the source doesn't give one; the simulator fills in `max(4, 0.08 × adp)`.
- `proj` — season total in the league's scoring, built by `scripts/scoring.py` or by hand.
- `pos` — one of QB, RB, WR, TE, K, DEF (`DST`, `D/ST`, and `PK` are accepted and normalized).
- `bye` and `note` are optional and may be omitted entirely; the six-column form `name,pos,team,adp,adp_sd,proj` is enough for every script.
- Include at least `teams × 15` players plus every relevant K and DEF, or the simulator will run out of bodies in late rounds.
