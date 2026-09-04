#!/usr/bin/env python3
"""
build_board.py — render the draft-day board (a single HTML file) from the simulator output,
your written notes, and the league config. Team colors for all 32 NFL teams are built in.

Usage:
  python3 build_board.py --league league.yaml --sim sim.json --notes notes.json \
      --players players.csv --out draft-board.html

notes.json schema: see references/output-spec.md §3. Everything in it is prose you wrote;
the renderer fills in projections, surplus, ADP, and availability from sim.json / players.csv
(and sim_availability.csv next to sim.json, for "still there at your NEXT pick").

The board is built for a phone on the clock. Top to bottom: one-line instructions (full steps behind a
disclosure) · the plan — your target at every pick with a Plan B · the position roadmap (where surplus
lives at each of your picks) · the four replacement numbers · your picks in order, five rows each with
"Next" (how often he's still there at your next pick; under 50% = take him now) · tier boards with
cliffs · shortlist verdicts · appendix. Tap a row when someone else takes a player; tap ✓ when you take
him — the footer lineup strip fills in, the nav advances to your next pick, and everything is saved in
the browser so a reload loses nothing.
"""
from __future__ import annotations

import argparse
import csv
import html
import json
import re
from pathlib import Path

TEAM_COLORS = {
    "ARI": ("#97233F", "#000000", "#FFB612"), "ATL": ("#A71930", "#000000", "#A5ACAF"),
    "BAL": ("#241773", "#000000", "#9E7C0C"), "BUF": ("#00338D", "#C60C30", "#E8B21A"),
    "CAR": ("#0085CA", "#101820", "#BFC0BF"), "CHI": ("#0B162A", "#C83803", "#F5A623"),
    "CIN": ("#FB4F14", "#000000", "#F2C14E"), "CLE": ("#311D00", "#FF3C00", "#F2C14E"),
    "DAL": ("#003594", "#041E42", "#B0B7BC"), "DEN": ("#FB4F14", "#002244", "#F2C14E"),
    "DET": ("#0076B6", "#B0B7BC", "#F2C14E"), "GB": ("#203731", "#FFB612", "#FFB612"),
    "HOU": ("#03202F", "#A71930", "#F2C14E"), "IND": ("#002C5F", "#A2AAAD", "#F2C14E"),
    "JAX": ("#006778", "#101820", "#D7A22A"), "KC": ("#E31837", "#FFB81C", "#FFB81C"),
    "LV": ("#000000", "#A5ACAF", "#A5ACAF"), "LAC": ("#0080C6", "#FFC20E", "#FFC20E"),
    "LAR": ("#003594", "#FFA300", "#FFD100"), "MIA": ("#008E97", "#FC4C02", "#F58220"),
    "MIN": ("#4F2683", "#FFC62F", "#FFC62F"), "NE": ("#002244", "#C60C30", "#B0B7BC"),
    "NO": ("#101820", "#D3BC8D", "#D3BC8D"), "NYG": ("#0B2265", "#A71930", "#A5ACAF"),
    "NYJ": ("#125740", "#000000", "#F2C14E"), "PHI": ("#004C54", "#A5ACAF", "#ACC0C6"),
    "PIT": ("#101820", "#FFB612", "#FFB612"), "SF": ("#AA0000", "#B3995D", "#B3995D"),
    "SEA": ("#002244", "#69BE28", "#A5ACAF"), "TB": ("#D50A0A", "#34302B", "#FF7900"),
    "TEN": ("#0C2340", "#4B92DB", "#C8102E"), "WAS": ("#5A1414", "#FFB612", "#FFB612"),
    "WSH": ("#5A1414", "#FFB612", "#FFB612"), "JAC": ("#006778", "#101820", "#D7A22A"),
}
POS_NAMES = {"RB": "Running back", "WR": "Wide receiver", "TE": "Tight end", "QB": "Quarterback", "K": "Kicker", "DEF": "Defense"}
AMBER = "#B7791F"


def hex_to_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def rgb_to_hex(rgb):
    return "#%02X%02X%02X" % tuple(max(0, min(255, int(round(c)))) for c in rgb)


def darken(h, f=0.35):
    r, g, b = hex_to_rgb(h)
    return rgb_to_hex((r * (1 - f), g * (1 - f), b * (1 - f)))


def lighten(h, f=0.85):
    r, g, b = hex_to_rgb(h)
    return rgb_to_hex((r + (255 - r) * f, g + (255 - g) * f, b + (255 - b) * f))


def luminance(h):
    r, g, b = [c / 255 for c in hex_to_rgb(h)]
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def theme_from(cfg: dict) -> dict:
    t = cfg.get("theme") or {}
    team = (t.get("team") or "custom").upper()
    if team == "CUSTOM" or team not in TEAM_COLORS:
        c = t.get("custom") or {}
        primary, secondary, accent = c.get("primary", "#00338D"), c.get("secondary", "#C60C30"), c.get("accent", "#E8B21A")
    else:
        primary, secondary, accent = TEAM_COLORS[team]
    sec_text = secondary if luminance(secondary) < 0.5 else darken(secondary, 0.45)
    if luminance(secondary) < 0.08:
        sec_text = "#333333"
    return {
        "primary": primary, "field": darken(primary, 0.4), "secondary": secondary, "sec_text": sec_text, "accent": accent,
        "ice": lighten(primary, 0.93), "ice_line": lighten(primary, 0.80), "sec_wash": lighten(secondary, 0.92),
        "sec_line": lighten(secondary, 0.75), "ladder_text": lighten(primary, 0.65), "ladder_sub": lighten(primary, 0.45),
        "mast_text": "#101C33" if luminance(primary) > 0.55 else "#FFFFFF", "rgb": ",".join(str(c) for c in hex_to_rgb(primary)),
    }


def load_players(path):
    out = {}
    with open(path, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r.get("name"):
                out[r["name"].strip()] = r
    return out


def load_matrix(sim_path):
    """name -> {pick: there%} from sim_availability.csv, if present next to sim.json."""
    p = Path(sim_path).with_name(Path(sim_path).stem + "_availability.csv")
    if not p.exists():
        return {}
    out = {}
    with open(p, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            d = {}
            for k, v in r.items():
                if k and k.startswith("there@"):
                    try:
                        d[int(k[6:])] = int(v)
                    except ValueError:
                        pass
            out[r["name"]] = d
    return out


def esc(s):
    return html.escape(str(s if s is not None else ""))


def lineup_total(plan_players, slots):
    byp = {}
    for pos, proj in plan_players:
        byp.setdefault(pos, []).append(proj)
    for k in byp:
        byp[k].sort(reverse=True)
    total = 0.0
    for s in slots:
        cands = ["RB", "WR", "TE"] if s == "FLEX" else ["QB", "RB", "WR", "TE"] if s == "SFLEX" else [s]
        best_pos, best = None, None
        for pos in cands:
            if byp.get(pos) and (best is None or byp[pos][0] > best):
                best, best_pos = byp[pos][0], pos
        if best is not None:
            total += best
            byp[best_pos].pop(0)
    return total


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--league", required=True)
    ap.add_argument("--sim", required=True)
    ap.add_argument("--notes", required=True)
    ap.add_argument("--players", required=True)
    ap.add_argument("--out", default="draft-board.html")
    ap.add_argument("--top", type=int, default=5, help="rows shown per pick before the 'more' expander")
    ap.add_argument("--max-pick", type=int, default=None, help="last pick to show a table for (default: through round 9)")
    args = ap.parse_args()

    cfgp = Path(args.league)
    if cfgp.suffix.lower() == ".json":
        cfg = json.loads(cfgp.read_text(encoding="utf-8"))
    else:
        import yaml  # type: ignore
        cfg = yaml.safe_load(cfgp.read_text(encoding="utf-8"))
    sim = json.loads(Path(args.sim).read_text(encoding="utf-8"))
    notes = json.loads(Path(args.notes).read_text(encoding="utf-8"))
    players = load_players(args.players)
    matrix = load_matrix(args.sim)
    th = theme_from(cfg)
    repl = sim["replacement"]
    targets = set(notes.get("mine") or [])
    teams = sim["league"]["teams"]
    rounds = sim["league"]["rounds"]
    keeper = sim["league"].get("keeper")
    max_pick = args.max_pick or teams * 9
    roster = cfg.get("roster", {}) or {}
    slots = []
    for pos in ("QB", "RB", "WR", "TE"):
        slots += [pos] * int(roster.get(pos, 0))
    slots += ["FLEX"] * int(roster.get("FLEX", 0)) + ["SFLEX"] * int(roster.get("SUPERFLEX", 0))
    slots += ["K"] * int(roster.get("K", 0)) + ["DEF"] * int(roster.get("DEF", 0))
    ladder = sim["ladder"]
    my_picks = [l["pick"] for l in ladder]
    round_of = {str(l["pick"]): l["round"] for l in ladder}
    avail = sim.get("availability", {})

    def pinfo(name):
        p = players.get(name, {})
        pos = p.get("pos", "?")
        proj = float(p.get("proj", 0) or 0)
        return pos, proj, round(proj - float(repl.get(pos, 0) or 0)), p.get("team", ""), round(float(p.get("adp", 0) or 0))

    def there_at(name, pk):
        m = matrix.get(name)
        if m and pk in m:
            return m[pk]
        for r in avail.get(str(pk), []):
            if r["name"] == name:
                return r["there"]
        return None

    def next_pick_of(pk):
        i = my_picks.index(pk) if pk in my_picks else -1
        return my_picks[i + 1] if 0 <= i < len(my_picks) - 1 else None

    def badge(pos):
        return f'<span class="pos {esc(pos)}">{esc(pos)}</span>'

    def me_btn(name):
        return f'<button type="button" class="me" data-name="{esc(name)}" aria-label="I drafted {esc(name)}" title="I drafted him">✓</button>'

    def pct(v, hot_below=50, big=False):
        if v is None:
            return '<span class="pct">—</span>'
        cls = "pct hot" if v < hot_below else "pct"
        return f'<span class="{cls}{" big" if big else ""}">{v}%</span>'

    plan_pick_of = {}
    for r in notes.get("plan") or []:
        if r.get("player"):
            plan_pick_of[r["player"]] = str(r.get("pick", ""))

    def target_tag(name):
        if name in plan_pick_of and name != keeper:
            pk = plan_pick_of[name]
            return f'<span class="ttag">TARGET{(" · " + esc(pk)) if pk and pk.upper() != "KEEP" else ""}</span>'
        if name in targets and name != keeper:
            return '<span class="ttag">TARGET</span>'
        return ""

    # ---------- plan ----------
    plan = notes.get("plan")
    if not plan:
        plan = [{"pick": r.get("pick"), "player": r.get("player"), "alt": r.get("alt", "")} for r in ((notes.get("target_build") or {}).get("rows") or [])]
    plan_rows = []
    for r in plan:
        name = r.get("player") or ""
        pk = str(r.get("pick", ""))
        pos, proj, vor, team, adp = pinfo(name)
        rd = round_of.get(pk)
        is_keep = pk.upper() == "KEEP"
        th_ = there_at(name, int(pk)) if pk.isdigit() else None
        alt = r.get("alt") or ""
        note = r.get("note") or ""
        plan_rows.append(
            f'<div class="prow" data-name="{esc(name)}">'
            f'<div class="ppick"><b>{"KEEP" if is_keep else esc(pk)}</b>{f"<s>rd {rd}</s>" if rd else ""}</div>'
            f'<div class="pmain"><div class="pname">{badge(pos)}<span class="nm">{esc(name)}</span>'
            f'<span class="psur">{vor:+d}</span>{pct(th_, big=True) if th_ is not None else ""}</div>'
            f'{"<div class=palt><b>If gone:</b> " + esc(alt) + "</div>" if alt else ""}'
            f'{"<div class=pnote>" + esc(note) + "</div>" if note else ""}</div>'
            f'</div>')
    plan_players = [(pinfo(r.get("player") or "")[0], pinfo(r.get("player") or "")[1]) for r in plan if (r.get("player") or "") in players]
    plan_total = lineup_total(plan_players, slots)
    mean = (sim.get("totals") or {}).get("mean")
    plan_total_lbl = notes.get("plan_total_label") or (f"{round(plan_total):,} projected starting points" + (f" · sim average {mean:,}" if mean else "") if plan_total else "")

    # ---------- roadmap ----------
    pp = sim.get("position_plan") or {}
    hm_rows, allvals = [], []
    for l in ladder:
        d = pp.get(str(l["pick"]))
        if d:
            allvals += [v for v in d.values() if isinstance(v, (int, float))]
    vmax = max(allvals) if allvals else 1
    for l in ladder:
        d = pp.get(str(l["pick"]))
        if not d or l["pick"] > max_pick:
            continue
        best = max(d, key=lambda k: d[k])
        cells = []
        for pos in ("QB", "RB", "WR", "TE"):
            v = d.get(pos)
            if v is None:
                cells.append("<td></td>")
                continue
            a = max(0.0, min(1.0, v / vmax)) if v > 0 else 0
            style = f'background:rgba({th["rgb"]},{0.07 + 0.5 * a:.2f})' if v > 0 else "background:#F2F4F8;color:#9AA5B8"
            cells.append(f'<td class="hm{" best" if pos == best else ""}" style="{style}">{v:+d}</td>')
        hm_rows.append(f'<tr><th>{l["pick"]}</th>{"".join(cells)}</tr>')
    ff = sim.get("flex_fill") or {}

    # ---------- pick blocks ----------
    pick_notes = notes.get("pick_notes") or {}

    def note_of(pk):
        v = pick_notes.get(str(pk)) or pick_notes.get(pk)
        if isinstance(v, dict):
            return v.get("note", ""), v.get("plan_b", "")
        return (v or ""), ""

    def show_pick(pk):
        return pk <= max_pick or bool(note_of(pk)[0])

    named = set(targets) | set(plan_pick_of)
    shortlisted = {s["player"] for s in (notes.get("shortlist") or []) if s.get("player")}

    def row_html(r, pk, nxt):
        name = r["name"]
        pos, proj, vor, team, adp = pinfo(name)
        nx = there_at(name, nxt) if nxt else None
        dim = " dim" if r["surplus"] <= 6 else ""
        hot = nx is not None and nx < 50 and r["there"] >= 50  # available now, probably gone by your next turn
        nx_html = ('<span class="pct">—</span>' if nx is None else
                   f'<span class="pct {"hot" if hot else "big"}">{nx}%</span>')
        return (f'<tr data-name="{esc(name)}" class="{dim.strip()}"><td class="pl"><div class="pcell">{badge(r["pos"])}<div class="pcol"><span class="nm">{esc(name)}</span>'
                f'<span class="meta">{esc(team)} · adp {adp}{target_tag(name)}</span></div></div></td>'
                f'<td class="n"><span class="sur{" strong" if r["surplus"] >= 60 else ""}">{r["surplus"]:+d}</span></td>'
                f'<td class="n"><span class="pct faint">{r["there"]}%</span></td>'
                f'<td class="n">{nx_html}</td>'
                f'<td class="act">{me_btn(name)}</td></tr>')

    blocks = []
    for idx, l in enumerate(ladder):
        pk = l["pick"]
        if not show_pick(pk):
            continue
        nxt = next_pick_of(pk)
        all_rows = avail.get(str(pk), [])
        rows = [r for r in all_rows if not r.get("watch") or r["there"] >= 1][: args.top + 5]
        note, plan_b = note_of(pk)
        shown = {r["name"] for r in rows}
        extras = []
        for r in all_rows:
            if r["name"] in shown:
                continue
            in_note = r["name"] in note or r["name"] in plan_b
            adp = float(players.get(r["name"], {}).get("adp", 0) or 0)
            in_play = 5 <= r["there"] <= 92 and adp <= pk + 1.5 * teams
            if in_note or ((r["name"] in named or r["name"] in shortlisted) and in_play):
                extras.append((0 if in_note else 1, -r["surplus"], r))
        extras.sort(key=lambda t: (t[0], t[1]))
        for _, _, r in extras[:4]:
            rows.append(r)
        rows.sort(key=lambda r: -r["surplus"])
        # named players (decision sentence / plan B) must be inside the visible top-N
        top, rest = rows[: args.top], rows[args.top:]
        promote = [r for r in rest if r["name"] in note or r["name"] in plan_b or r["name"] in plan_pick_of]
        for r in promote:
            rest.remove(r)
            top.append(r)
        top.sort(key=lambda r: -r["surplus"])
        if not top:
            continue
        trs = "".join(row_html(r, pk, nxt) for r in top)
        more = ""
        if rest:
            more = (f'<tbody class="more" hidden>{"".join(row_html(r, pk, nxt) for r in rest)}</tbody>'
                    f'<tbody><tr class="morerow"><td colspan="5"><button type="button" class="morebtn">{len(rest)} more</button></td></tr></tbody>')
        pb = f'<div class="planb"><b>If he\'s gone:</b> {esc(plan_b)}</div>' if plan_b else ""
        nxt_lbl = f'Next: {nxt}' if nxt else "Last pick"
        blocks.append(f'''
    <div class="pick" id="p{pk}" data-pick="{pk}">
      <div class="pickhd">
        <div class="jersey"><b>{pk}</b><s>RD {l["round"]}</s></div>
        <div class="picknote"><div class="decision">{esc(note) or "Best surplus on the board."}</div>{pb}</div>
      </div>
      <table>
        <thead><tr><th>Player</th><th class="n">Surplus</th><th class="n" title="Still there at this pick">Here</th><th class="n" title="Still there at your next pick">{esc(nxt_lbl)}</th><th class="act"></th></tr></thead>
        <tbody>{trs}</tbody>{more}
      </table>
      <div class="tierlink">Nothing you like? <a href="#tiers">Tier boards →</a></div>
    </div>''')
    first_late = next((l["pick"] for l in ladder if not show_pick(l["pick"])), None)
    late_block = f'''
    <div class="pick" id="late">
      <div class="pickhd">
        <div class="jersey"><b>{first_late or "late"}+</b><s>RD {(max_pick // teams) + 1}–{rounds}</s></div>
        <div class="picknote"><div class="decision">{esc(notes.get("late_note", "Nothing back here moves your lineup. Kicker and defense in the final two rounds only."))}</div></div>
      </div>
      <details class="latebody"><summary>Late-round plan</summary><p>{esc(notes.get("late_body", ""))}</p></details>
    </div>'''

    # ---------- tiers ----------
    tier_html, tier_tabs = [], []
    for pos, tdata in (notes.get("tiers") or {}).items():
        tier_tabs.append(f'<a href="#tier-{esc(pos)}">{esc(pos)}</a>')
        bands = []
        for b in tdata.get("bands", []):
            if "cliff" in b:
                bands.append(f'<div class="cliff"><b>{esc(b["cliff"])}</b><span>{esc(b.get("cliff_note", ""))}</span></div>')
            else:
                lbl = esc(b.get("label", ""))
                bnote = f' <span>— {esc(b["note"])}</span>' if b.get("note") else ""
                lis = []
                for n in b.get("players", []):
                    ppos, proj, vor, team, adp = pinfo(n)
                    lis.append(f'<li data-name="{esc(n)}"><span class="pn">{esc(n)}{"<span class=ktag>KEEPER</span>" if n == keeper else target_tag(n)}</span>'
                               f'<span class="pa">{esc(team)} · adp {adp}</span><span class="pp">{round(proj)}</span><span class="ps{" strong" if vor >= 60 else ""}">{vor:+d}</span>{me_btn(n)}</li>')
                bands.append(f'<div class="bandhd">{lbl}{bnote}</div><ul class="plist">{"".join(lis)}</ul>')
        sub = tdata.get("subtitle") or f'replacement {repl.get(pos, "")} · {sim["replacement_rank"].get(pos, "")} start weekly'
        tier_html.append(f'<div class="tier" id="tier-{esc(pos)}"><div class="th"><span>{POS_NAMES.get(pos, pos)}</span><em>{esc(sub)}</em></div><div class="band">{"".join(bands)}</div></div>')

    # ---------- shortlist / vegas ----------
    sl = []
    for s in notes.get("shortlist") or []:
        pos, proj, vor, team, adp = pinfo(s["player"])
        sl.append(f'<tr data-name="{esc(s["player"])}"><td class="pl"><div class="pcell">{badge(pos)}<div class="pcol"><span class="nm">{esc(s["player"])}</span><span class="meta">{esc(team)} · adp {adp}</span></div></div></td>'
                  f'<td class="n"><span class="sur{" strong" if vor >= 60 else ""}">{vor:+d}</span></td><td><span class="tag {esc(s.get("tag", "ok"))}">{esc(s["call"])}</span></td><td class="act">{me_btn(s["player"])}</td></tr>')
    vg = "".join(f'<li><b>{esc(v["value"])}</b><span>{esc(v["text"])}</span></li>' for v in notes.get("vegas") or [])

    # ---------- appendix / header bits ----------
    ax = notes.get("appendix") or {}
    terms = "".join(f'<dt>{esc(t["term"])}</dt><dd>{esc(t["def"])}</dd>' for t in ax.get("terms", []))
    how = "".join(f"<li>{t}</li>" for t in ax.get("how_built", []))
    assum = "".join(f"<li>{t}</li>" for t in ax.get("assumptions", []))
    hr = notes.get("headline_rule") or {}
    hr_paras = "".join(f"<p>{p}</p>" for p in hr.get("paragraphs", []))
    # League settings only in the masthead; methodology chips (sims, ADP source, model) belong in the appendix.
    settings_line = " · ".join(c for c in notes.get("chips", []) if not re.search(r"sims?\b|replacement|ADP", c, re.I))
    title = notes.get("title") or cfg["league"].get("team_name", "Draft board")
    subtitle = notes.get("subtitle") or f'{cfg["league"].get("season", "")} draft board · pick {sim["league"]["slot"]} of {teams}'
    repo = notes.get("repo") or ax.get("repo") or "nicoandmelissa/fantasy-draft-analyst"
    howto = notes.get("howto") or [
        ("Before the draft", "Read the plan once: your target at every pick and the fallback if he's gone. The roadmap under it shows which position still has value at each of your turns."),
        ("On the clock", "Tap your pick in the top bar. Take the highest surplus still on the board, not the biggest name. <b>Next</b> is how often a player is still there at your following pick — under 50% (amber) means take him now or lose him."),
        ("Someone else drafts a player", "Tap his row. He greys out on every list. Undo is in the footer for a few seconds."),
        ("You draft a player", "Tap ✓ on his row. The footer lineup fills in, and the top bar moves to your next pick."),
    ]
    howto_html = "".join(f'<li><b>{i + 1}</b><div><h4>{esc(h)}</h4><p>{b}</p></div></li>' for i, (h, b) in enumerate(howto))
    ladder_links = '<a href="#plan" data-tab="plan">PLAN</a>' + "".join(
        f'<a href="#p{l["pick"]}" data-tab="{l["pick"]}" title="Round {l["round"]}">{l["pick"]}</a>' for l in ladder if show_pick(l["pick"]))
    ladder_links += '<a href="#late">LATE</a><a href="#names">CALLS</a><a href="#appx">NOTES</a>'
    strip_html = "".join(f'<span class="lslot" data-slot="{s}"><s>{"FLX" if s == "FLEX" else "SFX" if s == "SFLEX" else s}</s><b>·</b></span>' for s in slots)
    rnums = " ".join(f'<span><b>{repl.get(pos, "")}</b> {pos}{sim["replacement_rank"].get(pos, "")}</span>' for pos in ("RB", "WR", "TE", "QB") if pos in repl)
    replacement_json = json.dumps({k: v for k, v in repl.items()})
    players_json = json.dumps({n: {"pos": p.get("pos", "?"), "proj": round(float(p.get("proj", 0) or 0))} for n, p in players.items()})
    storage_key = "fda-" + re.sub(r"[^a-z0-9]+", "-", (title + "-" + subtitle).lower())[:60]

    page = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)} — {esc(subtitle)}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Oswald:wght@500;600;700&display=swap" rel="stylesheet">
<style>
  :root{{
    --royal:{th["primary"]}; --field:{th["field"]}; --red:{th["secondary"]}; --red-tx:{th["sec_text"]}; --chalk:#FFFFFF;
    --ice:{th["ice"]}; --ice-line:{th["ice_line"]}; --red-wash:{th["sec_wash"]}; --red-line:{th["sec_line"]};
    --slate:#5A6B85; --ink:#101C33; --gold:{th["accent"]}; --amber:{AMBER}; --amber-wash:#FFF4DD; --ladder:{th["ladder_text"]}; --ladder-sub:{th["ladder_sub"]}; --mast-text:{th["mast_text"]};
    --disp:"Oswald","Arial Narrow","Helvetica Neue Condensed",Impact,sans-serif;
    --body:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;
  }}
  *{{box-sizing:border-box}} html{{-webkit-text-size-adjust:100%;scroll-padding-top:52px}}
  body{{margin:0;background:var(--chalk);color:var(--ink);font-family:var(--body);font-size:15px;line-height:1.45;padding-bottom:64px}}
  .wrap{{max-width:780px;margin:0 auto}}
  .mast{{background:var(--royal);color:var(--mast-text);padding:14px 16px 12px}}
  .mast .club{{font-family:var(--disp);font-weight:700;font-size:28px;line-height:1;margin:0}}
  .mast .club span{{display:inline-block;color:var(--gold);font-size:13px;font-weight:500;letter-spacing:.05em;margin-left:10px;vertical-align:middle}}
  .settings{{font-size:12px;opacity:.85;margin-top:6px}}
  .stripe{{height:4px;background:var(--red)}}
  .ladwrap{{position:sticky;top:0;z-index:40;background:var(--field);border-bottom:3px solid var(--red);display:flex}}
  .ladder{{flex:1;display:flex;overflow-x:auto;scrollbar-width:none;scroll-snap-type:x proximity}}
  .ladder::-webkit-scrollbar{{display:none}}
  .ladder a,.ladpin{{flex:0 0 auto;color:var(--ladder);text-decoration:none;font-family:var(--disp);font-weight:600;font-size:17px;padding:7px 11px 6px;border-right:1px solid rgba(255,255,255,.12);scroll-snap-align:start;line-height:1.1}}
  .ladder a small{{display:block;font-family:var(--body);font-size:8.5px;font-weight:600;letter-spacing:.08em;color:var(--ladder-sub);text-transform:uppercase}}
  .ladder a.now{{background:var(--red);color:#fff;position:relative}} .ladder a.now::after{{content:"NOW";display:block;font-family:var(--body);font-size:8px;font-weight:700;letter-spacing:.1em;line-height:1;margin-top:1px}}
  .ladder a.done{{opacity:.4}}
  .ladder a:hover,.ladder a:focus{{background:rgba(255,255,255,.1);color:#fff}}
  .ladpin{{background:var(--royal);color:#fff;border-left:1px solid rgba(255,255,255,.2);box-shadow:-18px 0 14px -6px rgba(0,0,0,.45)}}
  /* one-line instructions */
  .quick{{background:var(--ice);border-bottom:1px solid var(--ice-line);padding:8px 16px;font-size:12.5px;color:#243654}}
  .quick summary{{cursor:pointer;list-style:none;display:flex;justify-content:space-between;gap:10px}} .quick summary::-webkit-details-marker{{display:none}}
  .quick summary b{{color:var(--ink)}} .quick summary em{{font-style:normal;color:var(--royal);font-weight:600;white-space:nowrap}}
  .quick ol{{list-style:none;margin:10px 0 2px;padding:0;display:grid;grid-template-columns:1fr;gap:8px}}
  .quick li{{display:flex;gap:9px;align-items:flex-start}}
  .quick li > b{{flex:0 0 22px;height:22px;border-radius:50%;background:var(--royal);color:var(--mast-text);font-family:var(--disp);font-size:13px;display:flex;align-items:center;justify-content:center}}
  .quick h4{{margin:1px 0 1px;font-size:13px}} .quick p{{margin:0;font-size:12.5px}}
  section{{padding:16px 16px 4px}}
  h2{{font-family:var(--disp);font-weight:700;font-size:22px;margin:0 0 2px;color:var(--royal)}}
  h2 + .sub{{color:var(--slate);font-size:13px;margin:0 0 10px;max-width:64ch}}
  h3{{font-family:var(--disp);font-weight:600;font-size:16px;margin:16px 0 6px;color:var(--ink)}}
  details.notes{{margin:6px 0 10px;font-size:13px;color:#243654}} details.notes summary{{cursor:pointer;color:var(--royal);font-weight:600;font-size:12.5px}}
  details.notes p{{margin:6px 0 0}}
  /* plan */
  .plan{{border:2px solid var(--royal);border-radius:3px;overflow:hidden;margin-bottom:8px}}
  .plan .rh{{background:var(--royal);color:var(--mast-text);padding:8px 12px;font-family:var(--disp);font-size:16px;font-weight:600;display:flex;justify-content:space-between;align-items:baseline;gap:8px}}
  .plan .rh em{{font-style:normal;font-size:12px;font-weight:500;opacity:.9;font-family:var(--body);text-align:right}}
  .prow{{display:flex;gap:10px;padding:8px 10px;border-bottom:1px solid #EDF1F8;align-items:flex-start}} .prow:last-child{{border-bottom:none}}
  .ppick{{flex:0 0 46px;font-family:var(--disp);font-weight:700;font-size:20px;color:var(--royal);line-height:1}} .ppick s{{display:block;text-decoration:none;font-family:var(--body);font-size:9px;font-weight:700;letter-spacing:.06em;color:var(--slate);margin-top:2px;text-transform:uppercase}}
  .pmain{{flex:1;min-width:0}}
  .pname{{display:flex;align-items:center;gap:8px;flex-wrap:wrap}} .pname .nm{{font-weight:600}}
  .psur{{font-family:var(--disp);font-weight:600;font-size:15px;color:var(--royal);margin-left:auto}}
  .palt{{font-size:12px;color:#243654;margin-top:2px;line-height:1.35}} .palt b{{color:var(--red-tx)}}
  .pnote{{font-size:11.5px;color:var(--slate);margin-top:1px}}
  /* roadmap */
  .road{{border:1px solid var(--ice-line);border-radius:3px;overflow:hidden;margin:10px 0 4px}}
  .road .th{{background:var(--field);color:#fff;padding:7px 12px;font-family:var(--disp);font-weight:600;font-size:15px;display:flex;justify-content:space-between;align-items:baseline;gap:8px}}
  .road .th em{{font-family:var(--body);font-style:normal;font-size:11px;color:var(--ladder);font-weight:400;text-align:right}}
  .road table{{font-size:13.5px}} .road tbody th{{font-family:var(--disp);font-size:15px;color:var(--royal);text-align:left;padding:6px 10px;border-bottom:1px solid #EDF1F8;width:52px}}
  .road thead th{{font-family:var(--body);font-size:10.5px;letter-spacing:.07em;color:var(--slate);text-align:center;padding:6px 4px;border-bottom:1px solid var(--ice-line)}}
  .road td.hm{{text-align:center;font-variant-numeric:tabular-nums;padding:7px 4px;border-bottom:1px solid #EDF1F8;font-weight:500}}
  .road td.hm.best{{font-weight:700;color:var(--royal);box-shadow:inset 0 0 0 2px var(--royal)}}
  .road .cap{{margin:0;padding:7px 12px;font-size:11.5px;color:var(--slate);border-top:1px solid var(--ice-line)}}
  .road .read{{margin:0;padding:4px 12px 10px;font-size:12.5px;color:#243654;line-height:1.4}}
  .rnums{{display:flex;flex-wrap:wrap;gap:6px 14px;font-size:12.5px;color:var(--slate);margin:10px 0 2px;align-items:baseline}}
  .rnums b{{font-family:var(--disp);font-size:17px;color:var(--royal);margin-right:3px}} .rnums .lbl{{font-weight:600;color:var(--ink)}}
  /* picks */
  .pick{{border-top:1px solid var(--ice-line);padding:0 0 4px;scroll-margin-top:52px}} .pick:first-of-type{{border-top:none}}
  .pickhd{{display:flex;align-items:stretch}}
  .jersey{{flex:0 0 66px;background:var(--royal);color:var(--mast-text);text-align:center;padding:8px 0 6px;border-bottom:4px solid var(--red)}}
  .jersey b{{display:block;font-family:var(--disp);font-weight:700;font-size:32px;line-height:.9}}
  .jersey s{{display:block;text-decoration:none;font-size:9px;font-weight:700;letter-spacing:.1em;opacity:.75;margin-top:2px}}
  .picknote{{flex:1;padding:8px 12px;background:var(--ice);border-bottom:1px solid var(--ice-line);font-size:13.5px;color:#1B2C4A;display:flex;flex-direction:column;justify-content:center}}
  .decision{{font-weight:500}} .planb{{font-size:12.5px;color:#243654;margin-top:3px}} .planb b{{color:var(--red-tx)}}
  .tierlink{{font-size:12px;color:var(--slate);padding:6px 8px 2px;text-align:right}} .tierlink a{{color:var(--royal);font-weight:600;text-decoration:none}}
  .latebody{{padding:8px 6px;font-size:13.5px;color:#243654}} .latebody summary{{cursor:pointer;color:var(--royal);font-weight:600;font-size:12.5px}}
  table{{width:100%;border-collapse:collapse;font-size:14px}}
  thead th{{text-align:left;font-size:10px;font-weight:700;letter-spacing:.07em;color:var(--slate);padding:6px 6px 4px;border-bottom:1px solid var(--ice-line);text-transform:uppercase}}
  thead th.n{{text-align:right}}
  tbody td{{padding:7px 6px;border-bottom:1px solid #EDF1F8;vertical-align:middle}} tbody td.n{{text-align:right;font-variant-numeric:tabular-nums;white-space:nowrap}}
  tbody tr[data-name]{{cursor:pointer;-webkit-tap-highlight-color:transparent}} tbody tr[data-name]:hover{{background:#F7FAFF}}
  tr.dim{{opacity:.55}}
  td.pl{{min-width:0;width:55%}} .pcell{{display:flex;align-items:flex-start;gap:0}} .pcol{{min-width:0;display:flex;flex-direction:column}}
  .meta{{display:block;font-size:11px;color:var(--slate);line-height:1.3;margin-top:1px}} .meta .ttag{{margin-left:6px;vertical-align:0}}
  .pct.faint{{color:#9AA5B8}}
  td.act,th.act{{width:48px;text-align:right;padding-right:4px}}
  .nm{{font-weight:600}}
  .pos{{display:inline-block;min-width:26px;text-align:center;font-size:10px;font-weight:700;letter-spacing:.05em;padding:2px 4px;border-radius:2px;margin-right:7px;color:#fff;vertical-align:1px}}
  .pos.RB{{background:var(--red-tx)}} .pos.WR{{background:var(--royal)}} .pos.TE{{background:#0E7C6B}} .pos.QB{{background:#5B3E9E}} .pos.K,.pos.DEF{{background:var(--slate)}}
  .sur{{font-family:var(--disp);font-weight:500;font-size:16px;color:#38507A}} .sur.strong{{font-weight:700;color:var(--royal)}}
  .pct{{font-size:12px;color:var(--slate);font-variant-numeric:tabular-nums;white-space:nowrap}}
  .pct.big{{font-size:14.5px;font-weight:700;color:var(--ink)}}
  td.pl .nm{{overflow-wrap:anywhere}}
  @media (max-width:420px){{ tbody td{{padding:7px 4px}} .sur{{font-size:15px}} .me{{width:34px;height:32px}} td.act,th.act{{width:38px}} }}
  .pct.hot{{background:var(--amber-wash);color:var(--amber);border:1px solid #F1D9A4;border-radius:10px;padding:1px 7px;font-weight:700}}
  .ttag{{display:inline-block;font-size:9px;font-weight:700;letter-spacing:.06em;color:var(--royal);border:1px solid var(--royal);border-radius:2px;padding:0 4px;margin-left:6px;vertical-align:2px}}
  .ktag{{display:inline-block;font-size:9px;font-weight:700;letter-spacing:.06em;color:#101C33;background:var(--gold);border-radius:2px;padding:1px 4px;margin-left:6px;vertical-align:2px}}
  .me{{font:inherit;width:40px;height:34px;border-radius:17px;border:1.5px solid var(--ice-line);background:#fff;color:var(--slate);cursor:pointer;font-size:15px;line-height:1;padding:0}}
  .me:hover{{border-color:var(--gold)}} [data-mine="1"] .me{{background:var(--gold);border-color:var(--gold);color:#101C33;font-weight:700}}
  tr.gone,li.gone,.prow.gone{{opacity:.32}} tr.gone .nm,li.gone .pn,.prow.gone .nm{{text-decoration:line-through}}
  tr[data-mine="1"],li[data-mine="1"],.prow[data-mine="1"]{{background:#FFF8E1;box-shadow:inset 3px 0 0 var(--gold)}}
  body.hidegone tr.gone,body.hidegone li.gone{{display:none}}
  .morerow td{{padding:4px 6px 8px}} .morebtn{{font:inherit;font-size:12px;font-weight:600;color:var(--royal);background:var(--ice);border:1px solid var(--ice-line);border-radius:14px;padding:4px 12px;cursor:pointer}}
  /* tiers */
  .tiertabs{{position:sticky;top:44px;z-index:30;background:#fff;display:flex;gap:6px;padding:4px 0;border-bottom:1px solid var(--ice-line);margin-bottom:10px}}
  .tiertabs a{{font-family:var(--disp);font-weight:600;font-size:13px;color:var(--royal);text-decoration:none;border:1px solid var(--ice-line);border-radius:12px;padding:1px 10px;line-height:1.6}}
  .tier{{border:1px solid var(--ice-line);border-radius:3px;margin:0 0 16px;overflow:hidden;scroll-margin-top:96px}}
  .tier > .th{{background:var(--field);color:#fff;padding:7px 12px;font-family:var(--disp);font-weight:600;font-size:15px;display:flex;justify-content:space-between;align-items:baseline}}
  .tier > .th em{{font-family:var(--body);font-style:normal;font-size:11px;color:var(--ladder);font-weight:400}}
  .band{{padding:4px 12px 2px}}
  .bandhd{{font-size:10.5px;font-weight:700;letter-spacing:.06em;color:var(--royal);padding:8px 0 3px;text-transform:uppercase}}
  .bandhd span{{color:var(--slate);font-weight:600;letter-spacing:0;text-transform:none;font-size:11.5px}}
  .cliff{{display:flex;align-items:center;gap:9px;margin:8px -12px;padding:5px 12px;background:var(--red-wash);border-top:2px solid var(--red);border-bottom:1px solid var(--red-line)}}
  .cliff b{{font-family:var(--disp);font-size:15px;color:var(--red-tx)}} .cliff span{{font-size:12px;color:var(--red-tx)}}
  .plist{{margin:0;padding:0;list-style:none}}
  .plist li{{display:flex;align-items:center;gap:8px;padding:3px 0;border-bottom:1px solid #F1F5FB;font-size:13.5px;cursor:pointer}}
  .plist li:last-child{{border-bottom:none}}
  .plist .pn{{flex:1;font-weight:600;min-width:0}} .plist .pa{{color:var(--slate);font-size:11px;font-variant-numeric:tabular-nums;white-space:nowrap}}
  .plist .pp{{font-family:var(--disp);font-weight:500;font-variant-numeric:tabular-nums;white-space:nowrap;min-width:28px;text-align:right;color:#38507A}}
  .plist .ps{{font-family:var(--disp);font-weight:500;font-size:14px;min-width:34px;text-align:right;color:#38507A}} .plist .ps.strong{{font-weight:700;color:var(--royal)}}
  .verd td:nth-child(3){{white-space:nowrap}}
  .tag{{display:inline-block;padding:2px 7px;border-radius:2px;font-size:11px;font-weight:700;letter-spacing:.04em;color:#fff}}
  .tag.take{{background:#0E7C6B}} .tag.ok{{background:var(--royal)}} .tag.pass{{background:var(--red-tx)}}
  .vg{{margin:0;padding:0;list-style:none}}
  .vg li{{display:grid;grid-template-columns:78px 1fr;gap:10px;padding:8px 0;border-bottom:1px solid #EDF1F8;font-size:13px}}
  .vg b{{font-family:var(--disp);font-weight:600;font-size:15px;color:var(--royal);line-height:1.2}}
  .appx{{background:var(--field);color:#DCE6F7;padding-bottom:34px}}
  .appx h2{{color:#fff}} .appx h2 + .sub{{color:var(--ladder)}}
  .appx h3{{color:var(--gold);border-bottom:1px solid rgba(255,255,255,.16);padding-bottom:5px}}
  .appx dl{{display:grid;grid-template-columns:1fr;gap:12px;margin:0}}
  .appx dt{{font-weight:700;color:#fff;font-size:14px}} .appx dd{{margin:2px 0 0;font-size:13.5px;color:#C6D5EE}}
  .appx ul{{margin:8px 0 0;padding-left:20px;font-size:13.5px;color:#C6D5EE}} .appx li{{margin-bottom:7px}}
  .appx .warn{{border-left:3px solid var(--red);padding:2px 0 2px 12px;margin:14px 0;color:#F3C9D2;font-size:13.5px}}
  /* footer */
  .tools{{position:fixed;bottom:0;left:0;right:0;z-index:50;background:var(--field);border-top:3px solid var(--red);display:flex;align-items:center;gap:8px;padding:6px 10px;color:#fff;font-size:12px}}
  .strip{{flex:1;display:flex;gap:4px;overflow-x:auto;scrollbar-width:none}} .strip::-webkit-scrollbar{{display:none}}
  .lslot{{flex:0 0 auto;text-align:center;min-width:34px;padding:2px 4px;border-radius:3px;border:1px solid rgba(255,255,255,.18);line-height:1.1}}
  .lslot s{{display:block;text-decoration:none;font-size:8.5px;font-weight:700;letter-spacing:.06em;color:var(--ladder-sub)}} .lslot b{{display:block;font-size:11px;color:#fff;max-width:64px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}}
  .lslot.filled{{background:var(--gold);border-color:var(--gold)}} .lslot.filled s,.lslot.filled b{{color:#101C33}}
  .tools button{{font:inherit;font-weight:600;background:transparent;color:#fff;border:1px solid rgba(255,255,255,.4);border-radius:2px;padding:5px 9px;cursor:pointer;white-space:nowrap}}
  .tools button:hover,.tools button.on{{background:var(--red);border-color:var(--red)}}
  .tools details{{position:relative}} .tools summary{{list-style:none;cursor:pointer;font-weight:700;padding:4px 9px;border:1px solid rgba(255,255,255,.4);border-radius:2px}} .tools summary::-webkit-details-marker{{display:none}}
  .tools details div{{position:absolute;bottom:34px;right:0;background:var(--field);border:1px solid rgba(255,255,255,.3);padding:6px;display:flex;flex-direction:column;gap:6px}}
  #undo{{display:none;background:var(--gold);color:#101C33;border-color:var(--gold)}} #undo.show{{display:inline-block}}
  .credit{{text-align:center;font-size:11.5px;color:var(--slate);padding:14px 18px 24px}} .credit a{{color:var(--royal)}}
  @media (min-width:640px){{.mast .club{{font-size:34px}} .appx dl{{grid-template-columns:1fr 1fr;gap:14px 26px}} .quick ol{{grid-template-columns:1fr 1fr;gap:10px 22px}}}}
  @media print{{
    .ladwrap,.tools,.me,.tierlink,.morerow,.quick{{display:none}} tbody.more{{display:table-row-group!important}} body{{padding-bottom:0;font-size:10.5pt}} .wrap{{max-width:none}}
    *{{-webkit-print-color-adjust:exact;print-color-adjust:exact}} details{{display:block}} details > *{{display:block}} summary{{display:none}}
    .pagebreak{{break-before:page;page-break-before:always}} .tier,.pick,.plan,.road{{break-inside:avoid;page-break-inside:avoid}}
  }}
</style>
</head>
<body>
<div class="wrap">
  <header class="mast">
    <h1 class="club">{esc(title)}<span>{esc(subtitle)}</span></h1>
    {"<div class=settings>" + esc(settings_line) + "</div>" if settings_line else ""}
  </header>
  <div class="stripe"></div>
  <div class="ladwrap"><nav class="ladder" aria-label="Jump to a pick">{ladder_links}</nav><a class="ladpin" href="#tiers">TIERS</a></div>

  <details class="quick">
    <summary><span>Tap a row when he's <b>taken</b> · tap ✓ when he's <b>yours</b> · <b>amber %</b> = take him now</span><em>How this works</em></summary>
    <ol>{howto_html}</ol>
  </details>

  <section id="plan">
    <h2>The plan</h2>
    <p class="sub">{esc(notes.get("plan_sub", "Your target at every pick, the surplus he adds, how often he's still there, and the fallback if he's gone."))}</p>
    <div class="plan">
      <div class="rh"><span>Target build</span><em>{esc(plan_total_lbl)}</em></div>
      {"".join(plan_rows)}
    </div>
    {"<details class=notes><summary>Why this build</summary><p>" + esc(notes.get("target_note", "")) + "</p></details>" if notes.get("target_note") else ""}

    <div class="road">
      <div class="th"><span>Where the value is at each of your picks</span><em>best surplus still available, by position</em></div>
      <table>
        <thead><tr><th style="text-align:left">Pick</th><th>QB</th><th>RB</th><th>WR</th><th>TE</th></tr></thead>
        <tbody>{"".join(hm_rows)}</tbody>
      </table>
      <p class="cap">Outlined = best position at that pick · grey = nothing above replacement{(" · flex slots fill RB " + str(ff.get("RB", 0)) + " / WR " + str(ff.get("WR", 0)) + " / TE " + str(ff.get("TE", 0))) if ff else ""}</p>
      {"<p class=read>" + esc(notes.get("roadmap_note", "")) + "</p>" if notes.get("roadmap_note") else ""}
    </div>

    <div class="rnums"><span class="lbl">Replacement level</span>{rnums}</div>
    <details class="notes"><summary>{esc(hr.get("heading", "Why replacement level is the number that matters"))}</summary>{hr_paras or "<p>Replacement level is the projection of the worst player at each position who still has to start for someone every week. Every player's value is his projection minus that number — the Surplus column. Draft the biggest surplus, not the biggest projection.</p>"}</details>
  </section>

  <section id="picks" class="pagebreak">
    <h2>Your picks, in order</h2>
    <p class="sub">Ranked by surplus. <b>Next</b> = how often he's still there at your following pick; <b>amber</b> = available now, probably gone by then.</p>
    {"".join(blocks)}
    {late_block}
  </section>

  <section id="tiers" class="pagebreak">
    <h2>Tier boards</h2>
    <p class="sub">Grouped by real scoring gaps. A colored bar is a cliff — the point drop to the next tier. The right-hand number is surplus.</p>
    <div class="tiertabs">{"".join(tier_tabs)}</div>
    {"".join(tier_html)}
  </section>

  <section id="names" class="pagebreak">
    <h2>Calls on your shortlist</h2>
    <p class="sub">{esc(notes.get("shortlist_sub", "The names you flagged, run through the same surplus math."))}</p>
    <table class="verd">
      <thead><tr><th>Player</th><th class="n">Surplus</th><th>Call</th><th class="act"></th></tr></thead>
      <tbody>{"".join(sl)}</tbody>
    </table>
    {"<details class=notes><summary>What the betting market thinks</summary><ul class='vg'>" + vg + "</ul></details>" if vg else ""}
  </section>

  <section id="appx" class="appx pagebreak">
    <h2>Appendix</h2>
    <p class="sub">Every number on this sheet, where it came from, and what it means.</p>
    <h3>Terms</h3>
    <dl>{terms}</dl>
    <h3>How the numbers were built</h3>
    <ul>{how}</ul>
    <h3>Assumptions worth knowing about</h3>
    <ul>{assum}</ul>
    {"<div class='warn'><b>The one assumption that could flip this whole board:</b> " + esc(ax.get("flip_warning")) + "</div>" if ax.get("flip_warning") else ""}
    {"<div class='warn' style='border-color:var(--gold);color:#F6E3AE'><b>Also worth remembering:</b> " + esc(ax.get("gold_warning")) + "</div>" if ax.get("gold_warning") else ""}
  </section>
  <p class="credit">Built with <a href="https://github.com/{esc(repo)}">fantasy-draft-analyst</a> — free and open source.</p>
</div>

<div class="tools">
  <div class="strip" id="strip">{strip_html}</div>
  <button type="button" id="undo">Undo</button>
  <button type="button" id="hide">Hide taken</button>
  <details><summary>⋯</summary><div><button type="button" id="prt">Print</button><button type="button" id="rst">Reset</button></div></details>
</div>

<script>
(function(){{
  var KEY = {json.dumps(storage_key)};
  var PLAYERS = {players_json};
  var REPL = {replacement_json};
  var SLOTS = {json.dumps(slots)};
  var KEEPER = {json.dumps(keeper)};
  var MYPICKS = {json.dumps(my_picks)};
  var gone = new Set(), mine = new Set(), history = [];
  if (KEEPER) mine.add(KEEPER);
  try {{ var saved = JSON.parse(localStorage.getItem(KEY) || 'null'); if (saved) {{ gone = new Set(saved.gone||[]); mine = new Set(saved.mine||[]); if (KEEPER) mine.add(KEEPER); }} }} catch(e) {{}}
  function save(){{ try {{ localStorage.setItem(KEY, JSON.stringify({{gone:[...gone], mine:[...mine]}})); }} catch(e) {{}} }}
  function snapshot(){{ history.push({{gone:[...gone], mine:[...mine]}}); if (history.length > 20) history.shift(); showUndo(); }}
  var undoTimer = null;
  function showUndo(){{ var u = document.getElementById('undo'); u.classList.add('show'); clearTimeout(undoTimer); undoTimer = setTimeout(function(){{ u.classList.remove('show'); }}, 5000); }}
  function rows(){{ return document.querySelectorAll('[data-name]'); }}
  function paint(){{
    rows().forEach(function(el){{
      var nm = el.getAttribute('data-name');
      var isMine = mine.has(nm), isGone = gone.has(nm) && !isMine;
      el.classList.toggle('gone', isGone);
      el.setAttribute('data-mine', isMine ? '1' : '0');
    }});
    lineup(); nav(); save();
  }}
  function lineup(){{
    var byPos = {{}};
    [...mine].forEach(function(n){{ var p = PLAYERS[n]; if(!p) return; (byPos[p.pos] = byPos[p.pos] || []).push({{name:n, proj:p.proj, pos:p.pos}}); }});
    Object.keys(byPos).forEach(function(k){{ byPos[k].sort(function(a,b){{return b.proj-a.proj;}}); }});
    var used = new Set(), fills = [];
    SLOTS.forEach(function(s){{
      var cands = s === 'FLEX' ? ['RB','WR','TE'] : s === 'SFLEX' ? ['QB','RB','WR','TE'] : [s];
      var best = null;
      cands.forEach(function(pos){{ (byPos[pos]||[]).forEach(function(p){{ if(!used.has(p.name) && (!best || p.proj > best.proj)) best = p; }}); }});
      if (best) used.add(best.name);
      fills.push(best);
    }});
    document.querySelectorAll('#strip .lslot').forEach(function(el, i){{
      var f = fills[i]; el.classList.toggle('filled', !!f);
      el.querySelector('b').textContent = f ? f.name.split(' ').slice(-1)[0] : '·';
      el.title = f ? f.name + ' (' + f.proj + ')' : 'open';
    }});
  }}
  function nav(){{
    var drafted = [...mine].filter(function(n){{ return n !== KEEPER; }}).length;
    var next = MYPICKS[drafted];
    document.querySelectorAll('.ladder a[data-tab]').forEach(function(a){{
      var t = a.getAttribute('data-tab'); if (t === 'plan') return;
      var pk = parseInt(t, 10);
      a.classList.toggle('now', pk === next);
      a.classList.toggle('done', MYPICKS.indexOf(pk) < drafted);
    }});
    var nowEl = document.querySelector('.ladder a.now');
    if (nowEl) {{ var lad = nowEl.parentElement; try {{ lad.scrollTo({{left: Math.max(0, nowEl.offsetLeft - 70), behavior: drafted > 0 ? 'smooth' : 'auto'}}); }} catch(e) {{}} }}
  }}
  document.addEventListener('click', function(e){{
    var mb = e.target.closest('.morebtn');
    if (mb) {{ var tb = mb.closest('table').querySelector('tbody.more'); tb.hidden = !tb.hidden; mb.textContent = tb.hidden ? mb.getAttribute('data-n') : 'Show fewer'; return; }}
    var btn = e.target.closest('.me');
    if (btn) {{ e.stopPropagation(); snapshot(); var nm = btn.getAttribute('data-name'); if (mine.has(nm) && nm !== KEEPER) mine.delete(nm); else {{ mine.add(nm); gone.delete(nm); }} paint(); return; }}
    var row = e.target.closest('[data-name]');
    if (row && !row.classList.contains('prow')) {{ var nm2 = row.getAttribute('data-name'); if (mine.has(nm2)) return; snapshot(); if (gone.has(nm2)) gone.delete(nm2); else gone.add(nm2); paint(); }}
  }});
  // remember the "N more" label
  document.querySelectorAll('.morebtn').forEach(function(b){{ b.setAttribute('data-n', b.textContent); }});
  document.addEventListener('keydown', function(e){{
    if ((e.key === 'Enter' || e.key === ' ') && e.target.matches('[data-name]')) {{ e.preventDefault(); e.target.click(); }}
  }});
  rows().forEach(function(el){{ if (!el.classList.contains('prow')) {{ el.setAttribute('tabindex','0'); el.setAttribute('role','button'); }} }});
  document.getElementById('undo').addEventListener('click', function(){{ var h = history.pop(); if (!h) return; gone = new Set(h.gone); mine = new Set(h.mine); if (KEEPER) mine.add(KEEPER); paint(); this.classList.remove('show'); }});
  document.getElementById('rst').addEventListener('click', function(){{ if (!confirm('Clear every taken / mine mark?')) return; gone.clear(); mine = new Set(KEEPER ? [KEEPER] : []); paint(); }});
  document.getElementById('prt').addEventListener('click', function(){{ window.print(); }});
  document.getElementById('hide').addEventListener('click', function(){{ document.body.classList.toggle('hidegone'); this.classList.toggle('on'); }});
  paint();
}})();
</script>
</body>
</html>
'''
    Path(args.out).write_text(page, encoding="utf-8")
    print(f"Wrote {args.out} ({len(page) // 1024} KB), theme {cfg.get('theme', {}).get('team', 'custom')}")


if __name__ == "__main__":
    main()
