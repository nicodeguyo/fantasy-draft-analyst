#!/usr/bin/env python3
"""
fetch_adp.py — pull current ADP into adp.csv from sources that work without a login.

Sources:
  ffc          FantasyFootballCalculator mock-draft ADP for a format and league size (gives std dev).
               --format {standard,ppr,half-ppr,2qb,dynasty,rookie} --teams {8,10,12,14}
  espn         ESPN's own ADP + default ranks + ESPN season projections (the market ESPN rooms draft in).
  footballguys Cross-platform table: one column per platform (ESPN, Yahoo, Sleeper, CBS, FFPC, NFFC, Underdog…).
               --platform picks the column to write as `adp`; all columns are kept in extra fields.
  sleeper-trending  What managers are adding/dropping right now (hype/injury signal), resolved to names.

Usage:
  python3 fetch_adp.py --source ffc --format half-ppr --teams 12 --out adp.csv
  python3 fetch_adp.py --source espn --out adp_espn.csv
  python3 fetch_adp.py --source footballguys --platform yahoo --out adp_yahoo.csv
  python3 fetch_adp.py --source sleeper-trending

Standard library only. Sites change their markup; when a parser fails, the script says so and tells you
which page to open by hand (Claude can read the page directly and write adp.csv itself).
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import sys
import urllib.request
from html.parser import HTMLParser

UA = "Mozilla/5.0 (fantasy-draft-analyst; +https://github.com/nicodeguyo/fantasy-draft-analyst)"


def get(url: str, headers: dict | None = None, timeout: int = 30) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": UA, **(headers or {})})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.read().decode("utf-8", errors="replace")
    except Exception as e:  # network blocked, site down, layout moved
        sys.exit(f"Could not fetch {url}\n  ({e})\n"
                 f"  If you're in a sandbox without web access, open the page in a browser (or let Claude fetch it) "
                 f"and paste the table into adp.csv with columns name,pos,team,adp,adp_sd.")


class TableParser(HTMLParser):
    """Collects every <table> as a list of rows of cell text."""

    def __init__(self):
        super().__init__()
        self.tables, self._t, self._row, self._cell, self._in_cell = [], None, None, [], False

    def handle_starttag(self, tag, attrs):
        if tag == "table":
            self._t = []
        elif tag == "tr" and self._t is not None:
            self._row = []
        elif tag in ("td", "th") and self._row is not None:
            self._in_cell, self._cell = True, []

    def handle_endtag(self, tag):
        if tag in ("td", "th") and self._in_cell:
            self._row.append(re.sub(r"\s+", " ", "".join(self._cell)).strip())
            self._in_cell = False
        elif tag == "tr" and self._row is not None:
            if self._row:
                self._t.append(self._row)
            self._row = None
        elif tag == "table" and self._t is not None:
            self.tables.append(self._t)
            self._t = None

    def handle_data(self, data):
        if self._in_cell:
            self._cell.append(data)


def norm_pos(p: str) -> str:
    p = p.upper().strip()
    return {"DST": "DEF", "D/ST": "DEF", "PK": "K", "DEF": "DEF"}.get(p, p)


# ---------------------------------------------------------------------------

def fetch_ffc(fmt: str, teams: int):
    fmt = fmt.lower()
    path = f"/adp/{teams}-team/all" if fmt == "standard" else f"/adp/{fmt}/{teams}-team/all"
    url = "https://fantasyfootballcalculator.com" + path
    html = get(url)
    m = re.search(r"Data from ([\d,]+) .*?mock drafts between (.+?)\.?</", html)
    note = f"FFC {fmt} {teams}-team, {m.group(1)} mocks, {m.group(2)}" if m else f"FFC {fmt} {teams}-team"
    tp = TableParser()
    tp.feed(html)
    rows = []
    for t in tp.tables:
        hdr = [h.lower() for h in t[0]]
        if "name" in hdr and "overall" in hdr:
            i_name, i_pos, i_team = hdr.index("name"), hdr.index("pos"), hdr.index("team")
            i_over, i_sd = hdr.index("overall"), hdr.index("std. dev") if "std. dev" in hdr else None
            i_bye = hdr.index("bye") if "bye" in hdr else None
            for r in t[1:]:
                if len(r) <= i_over:
                    continue
                try:
                    rows.append({"name": r[i_name], "pos": norm_pos(r[i_pos]), "team": r[i_team], "adp": float(r[i_over]),
                                 "adp_sd": float(r[i_sd]) if i_sd is not None else "", "bye": r[i_bye] if i_bye is not None else ""})
                except ValueError:
                    continue
            break
    if not rows:
        sys.exit(f"Could not parse the FFC table. Open {url} in a browser and copy the table into adp.csv (name,pos,team,adp,adp_sd).")
    return rows, note


def fetch_espn(season: int, limit: int = 350):
    url = f"https://lm-api-reads.fantasy.espn.com/apis/v3/games/ffl/seasons/{season}/segments/0/leaguedefaults/3?view=kona_player_info"
    flt = {"players": {"limit": limit, "sortDraftRanks": {"sortPriority": 100, "sortAsc": True, "value": "PPR"}}}
    data = json.loads(get(url, headers={"X-Fantasy-Filter": json.dumps(flt)}))
    pos_map = {1: "QB", 2: "RB", 3: "WR", 4: "TE", 5: "K", 16: "DEF"}
    team_map = {1: "ATL", 2: "BUF", 3: "CHI", 4: "CIN", 5: "CLE", 6: "DAL", 7: "DEN", 8: "DET", 9: "GB", 10: "TEN", 11: "IND", 12: "KC",
                13: "LV", 14: "LAR", 15: "MIA", 16: "MIN", 17: "NE", 18: "NO", 19: "NYG", 20: "NYJ", 21: "PHI", 22: "ARI", 23: "PIT",
                24: "LAC", 25: "SF", 26: "SEA", 27: "TB", 28: "WAS", 29: "CAR", 30: "JAX", 33: "BAL", 34: "HOU"}
    rows = []
    for item in data.get("players", []):
        p = item.get("player", item)
        own = p.get("ownership") or {}
        adp = own.get("averageDraftPosition")
        if not adp:
            continue
        ranks = p.get("draftRanksByRankType") or {}
        proj = ""
        for s in p.get("stats") or []:
            if s.get("seasonId") == season and s.get("statSourceId") == 1 and s.get("statSplitTypeId") == 0:
                proj = round(float(s.get("appliedTotal", 0)), 1)
        rows.append({"name": p.get("fullName"), "pos": pos_map.get(p.get("defaultPositionId"), "?"),
                     "team": team_map.get(p.get("proTeamId"), ""), "adp": round(float(adp), 1), "adp_sd": "",
                     "espn_rank_ppr": (ranks.get("PPR") or {}).get("rank", ""), "espn_rank_std": (ranks.get("STANDARD") or {}).get("rank", ""),
                     "espn_proj_ppr": proj, "injury": p.get("injuryStatus", ""), "pct_owned": round(float(own.get("percentOwned", 0)), 1)})
    if not rows:
        sys.exit("ESPN returned no players; the API may have changed. Fallback: Footballguys ESPN column.")
    return rows, f"ESPN ADP via lm-api-reads (kona_player_info), season {season}"


def fetch_footballguys(season: int, platform: str | None):
    url = f"https://www.footballguys.com/adp?season={season}&pos=all"
    html = get(url)
    tp = TableParser()
    tp.feed(html)
    best = max(tp.tables, key=len) if tp.tables else None
    if not best or len(best) < 5:
        sys.exit(f"Could not parse the Footballguys table. Open {url} and copy the column you need into adp.csv.")
    hdr = best[0]
    # find the player column and platform columns
    i_player = next((i for i, h in enumerate(hdr) if "player" in h.lower()), 0)
    cols = {h: i for i, h in enumerate(hdr)}
    key = None
    if platform:
        want = platform.lower()
        for h, i in cols.items():
            hl = h.lower().replace("!", "")
            if want == hl or want in hl:
                key = h
                break
        if key is None:
            sys.exit(f"No column matching '{platform}'. Columns: {', '.join(hdr)}")
    rows = []
    for r in best[1:]:
        if len(r) <= i_player:
            continue
        cell = r[i_player]
        m = re.match(r"(.+?)\s+(QB|RB|WR|TE|PK|K|DEF|DST|D/ST)\b\s*(\w{2,3})?", cell)
        name, pos, team = (m.group(1), norm_pos(m.group(2)), m.group(3) or "") if m else (cell, "", "")
        row = {"name": name.strip(), "pos": pos, "team": team}
        for h, i in cols.items():
            if i < len(r) and h and h.lower() not in ("player", "pos", "team", "#", "rank"):
                row[h.lower().replace("!", "").replace(" ", "_")] = r[i]
        if key:
            try:
                row["adp"] = float(r[cols[key]])
            except (ValueError, IndexError):
                continue
        rows.append(row)
    if not rows:
        sys.exit("Parsed the page but found no rows; the layout may have changed.")
    return rows, f"Footballguys cross-platform ADP, season {season}" + (f", platform column '{key}'" if key else "")


def fetch_sleeper_trending(kind: str = "add", hours: int = 24, limit: int = 25):
    trend = json.loads(get(f"https://api.sleeper.app/v1/players/nfl/trending/{kind}?lookback_hours={hours}&limit={limit}"))
    try:
        players = json.loads(get("https://api.sleeper.app/v1/players/nfl", timeout=120))
    except Exception:
        players = {}
    rows = []
    for t in trend:
        pid = str(t["player_id"])
        p = players.get(pid, {})
        rows.append({"player_id": pid, "name": p.get("full_name") or (pid + " (team DEF)" if pid.isalpha() else pid),
                     "pos": p.get("position", ""), "team": p.get("team", ""), "count": t["count"],
                     "injury": p.get("injury_status") or ""})
    return rows, f"Sleeper trending {kind}s, last {hours}h"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--source", required=True, choices=["ffc", "espn", "footballguys", "sleeper-trending"])
    ap.add_argument("--format", default="half-ppr")
    ap.add_argument("--teams", type=int, default=12)
    ap.add_argument("--season", type=int, default=2026)
    ap.add_argument("--platform", default=None, help="footballguys column to use as adp (espn, yahoo, sleeper, cbs, ffpc, nffc, underdog…)")
    ap.add_argument("--kind", default="add", choices=["add", "drop"])
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    if args.source == "ffc":
        rows, note = fetch_ffc(args.format, args.teams)
    elif args.source == "espn":
        rows, note = fetch_espn(args.season)
    elif args.source == "footballguys":
        rows, note = fetch_footballguys(args.season, args.platform)
    else:
        rows, note = fetch_sleeper_trending(args.kind)

    if args.out:
        fields = []
        for r in rows:
            for k in r:
                if k not in fields:
                    fields.append(k)
        with open(args.out, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=fields)
            w.writeheader()
            w.writerows(rows)
        print(f"Wrote {len(rows)} rows to {args.out} — source: {note}")
    else:
        print(f"# {note}")
        for r in rows[:40]:
            print(", ".join(f"{k}={v}" for k, v in r.items()))


if __name__ == "__main__":
    main()
