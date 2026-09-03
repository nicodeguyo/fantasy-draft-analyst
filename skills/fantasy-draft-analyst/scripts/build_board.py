#!/usr/bin/env python3
"""
build_board.py — render the draft-day board (a single HTML file) from the simulator output,
your written notes, and the league config. Team colors for all 32 NFL teams are built in.

Usage:
  python3 build_board.py --league league.yaml --sim sim.json --notes notes.json \
      --players players.csv --out draft-board.html

notes.json schema: see references/output-spec.md §3. Everything in it is prose you wrote;
the renderer fills in projections, surplus, ADP, and There % from sim.json / players.csv.

The board: sticky pick ladder, the replacement-level rule up top, top-N at each of your picks
ranked by surplus with There % bars, tier boards with cliffs, your shortlist with verdict tags,
Vegas notes, the target build, and an appendix. Tap any player to cross him off. Prints to ~4 pages.
"""
from __future__ import annotations

import argparse
import csv
import html
import json
import sys
from pathlib import Path

TEAM_COLORS = {
    # abbr: (primary, secondary, accent)
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
    # If the secondary is too dark to read as a highlight, keep it but use a readable dark variant for text.
    sec_text = secondary if luminance(secondary) < 0.5 else darken(secondary, 0.45)
    if luminance(secondary) < 0.08:  # near-black secondary: use a muted charcoal so cliffs still read
        sec_text = "#333333"
    return {
        "primary": primary, "field": darken(primary, 0.4), "secondary": secondary, "sec_dark": darken(secondary, 0.25),
        "sec_text": sec_text, "accent": accent, "ice": lighten(primary, 0.92), "ice_line": lighten(primary, 0.78),
        "sec_wash": lighten(secondary, 0.92), "sec_line": lighten(secondary, 0.75),
        "ladder_text": lighten(primary, 0.65), "ladder_sub": lighten(primary, 0.45),
        "primary_is_light": luminance(primary) > 0.55,
    }


def load_players(path):
    out = {}
    with open(path, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r.get("name"):
                out[r["name"].strip()] = r
    return out


def esc(s):
    return html.escape(str(s if s is not None else ""))


def sur_class(v):
    return "s-elite" if v >= 90 else "s-good" if v >= 70 else "s-ok" if v >= 40 else "s-meh"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--league", required=True)
    ap.add_argument("--sim", required=True)
    ap.add_argument("--notes", required=True)
    ap.add_argument("--players", required=True)
    ap.add_argument("--out", default="draft-board.html")
    ap.add_argument("--top", type=int, default=7)
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
    th = theme_from(cfg)
    repl = sim["replacement"]
    mine = set(notes.get("mine") or [])
    teams = sim["league"]["teams"]
    rounds = sim["league"]["rounds"]
    max_pick = args.max_pick or teams * 9
    # Players the notes talk about must never be hidden by the top-N cut: the target build and "mine"
    # always; shortlist players wherever they are genuinely in play (not a near-lock either way).
    named = set(mine)
    named.update(r["player"] for r in ((notes.get("target_build") or {}).get("rows") or []) if r.get("player"))
    shortlisted = {s["player"] for s in (notes.get("shortlist") or []) if s.get("player")}

    def prow(name, extra_cls=""):
        p = players.get(name, {})
        pos = p.get("pos", "?")
        vor = float(p.get("proj", 0)) - float(repl.get(pos, 0))
        return (f'<li class="{extra_cls}{" mine" if name in mine else ""}"><span class="pn">{esc(name)}'
                f'{" — yours" if name == sim["league"].get("keeper") else ""}</span>'
                f'<span class="pa">{esc(p.get("team", ""))} · adp {round(float(p.get("adp", 0)))}</span>'
                f'<span class="pp">{round(float(p.get("proj", 0)))}</span></li>')

    # ---------- ladder ----------
    ladder = sim["ladder"]
    pick_notes = notes.get("pick_notes") or {}

    def has_note(pk):
        return str(pk) in pick_notes or pk in pick_notes

    def show_pick(pk):
        return pk <= max_pick or has_note(pk)

    ladder_links = "".join(f'<a href="#p{l["pick"]}">{l["pick"]}<small>RD {l["round"]}</small></a>'
                           for l in ladder if show_pick(l["pick"]))
    ladder_links += '<a href="#late">LATE<small>DEPTH</small></a><a href="#tiers">TIERS<small>BY POS</small></a>' \
                    '<a href="#names">CALLS<small>TAKE/PASS</small></a><a href="#appx">NOTES<small>APPENDIX</small></a>'

    # ---------- pick blocks ----------
    blocks = []
    for l in ladder:
        pk = l["pick"]
        if not show_pick(pk):
            continue
        all_rows = sim["availability"].get(str(pk), [])
        rows = [r for r in all_rows if not r.get("watch") or r["there"] >= 1][: args.top]
        note_text = str(pick_notes.get(str(pk)) or pick_notes.get(pk) or "")
        shown = {r["name"] for r in rows}
        extras = []
        for r in all_rows:
            if r["name"] in shown:
                continue
            in_note = r["name"] in note_text
            adp = float(players.get(r["name"], {}).get("adp", 0) or 0)
            in_play = 5 <= r["there"] <= 92 and adp <= pk + 1.5 * teams
            if in_note or ((r["name"] in named or r["name"] in shortlisted) and in_play):
                extras.append((0 if in_note else 1, -r["surplus"], r))
        extras.sort(key=lambda t: (t[0], t[1]))
        for _, _, r in extras[:4]:
            rows.append(r)
            shown.add(r["name"])
        rows.sort(key=lambda r: -r["surplus"])
        if not rows:
            continue
        trs = []
        for r in rows:
            lo = " lo" if r["there"] < 50 else ""
            trs.append(f'<tr><td><span class="pos {r["pos"]}">{r["pos"]}</span><span class="nm">{esc(r["name"])}</span></td>'
                       f'<td class="n">{r["proj"]}</td><td class="n"><span class="sur {sur_class(r["surplus"])}">{r["surplus"]:+d}</span></td>'
                       f'<td class="n"><span class="bar{lo}"><i style="width:{r["there"]}%"></i></span><span class="pct">{r["there"]}%</span></td></tr>')
        note = pick_notes.get(str(pk)) or pick_notes.get(pk) or "Best surplus on the board."
        blocks.append(f'''
    <div class="pick" id="p{pk}">
      <div class="pickhd">
        <div class="jersey"><b>{pk}</b><s>ROUND {l["round"]}</s></div>
        <div class="picknote">{esc(note)}</div>
      </div>
      <table>
        <thead><tr><th>Player</th><th class="n">Proj</th><th class="n">Surplus</th><th class="n">There</th></tr></thead>
        <tbody>{"".join(trs)}</tbody>
      </table>
    </div>''')
    first_late = next((l["pick"] for l in ladder if not show_pick(l["pick"])), None)
    late_block = f'''
    <div class="pick" id="late">
      <div class="pickhd">
        <div class="jersey"><b>{first_late or "late"}+</b><s>RD {(max_pick // teams) + 1}–{rounds}</s></div>
        <div class="picknote">{esc(notes.get("late_note", "Nothing back here moves your lineup. Kicker and defense in the final two rounds only."))}</div>
      </div>
      <table><tbody><tr style="cursor:default"><td colspan="4" style="padding:12px 6px;font-size:13.5px;color:#243654">{esc(notes.get("late_body", ""))}</td></tr></tbody></table>
    </div>'''

    # ---------- tiers ----------
    tier_html = []
    for pos, tdata in (notes.get("tiers") or {}).items():
        bands = []
        for b in tdata.get("bands", []):
            if "cliff" in b:
                bands.append(f'<div class="cliff"><b>{esc(b["cliff"])}</b><span>{esc(b.get("cliff_note", ""))}</span></div>')
            else:
                lbl = esc(b.get("label", ""))
                note = f' <span>— {esc(b["note"])}</span>' if b.get("note") else ""
                lis = "".join(prow(n) for n in b.get("players", []))
                bands.append(f'<div class="bandhd">{lbl}{note}</div><ul class="plist">{lis}</ul>')
        name = {"RB": "Running back", "WR": "Wide receiver", "TE": "Tight end", "QB": "Quarterback", "K": "Kicker", "DEF": "Defense"}.get(pos, pos)
        sub = tdata.get("subtitle") or f'replacement {repl.get(pos, "")} · {sim["replacement_rank"].get(pos, "")} get started weekly'
        tier_html.append(f'<div class="tier"><div class="th"><span>{name}</span><em>{esc(sub)}</em></div><div class="band">{"".join(bands)}</div></div>')

    # ---------- shortlist / vegas / build ----------
    sl = []
    for s in notes.get("shortlist") or []:
        p = players.get(s["player"], {})
        pos = p.get("pos", "?")
        vor = round(float(p.get("proj", 0)) - float(repl.get(pos, 0)))
        sl.append(f'<tr><td><span class="pos {pos}">{pos}</span><span class="nm">{esc(s["player"])}</span></td><td class="n">{round(float(p.get("proj", 0)))}</td>'
                  f'<td class="n"><span class="sur {sur_class(vor)}">{vor:+d}</span></td><td><span class="tag {esc(s.get("tag", "ok"))}">{esc(s["call"])}</span></td></tr>')
    vg = "".join(f'<li><b>{esc(v["value"])}</b><span>{esc(v["text"])}</span></li>' for v in notes.get("vegas") or [])
    tb = notes.get("target_build") or {}
    tb_rows = []
    for r in tb.get("rows", []):
        p = players.get(r["player"], {})
        tb_rows.append(f'<tr><td class="rd">{esc(r["pick"])}</td><td><span class="pos {p.get("pos", "?")}">{p.get("pos", "?")}</span><span class="nm">{esc(r["player"])}</span></td><td class="n">{round(float(p.get("proj", 0)))}</td></tr>')

    # ---------- appendix ----------
    ax = notes.get("appendix") or {}
    terms = "".join(f'<dt>{esc(t["term"])}</dt><dd>{esc(t["def"])}</dd>' for t in ax.get("terms", []))
    how = "".join(f"<li>{t}</li>" for t in ax.get("how_built", []))
    assum = "".join(f"<li>{t}</li>" for t in ax.get("assumptions", []))
    hr = notes.get("headline_rule") or {}
    hot, cool = hr.get("hot", {}), hr.get("cool", {})
    hr_paras = "".join(f"<p>{p}</p>" for p in hr.get("paragraphs", []))
    chips = "".join(f'<span class="chip">{esc(c)}</span>' for c in notes.get("chips", []))
    title = notes.get("title") or cfg["league"].get("team_name", "Draft board")
    subtitle = notes.get("subtitle") or f'{cfg["league"].get("season", "")} draft board · pick {sim["league"]["slot"]} of {teams}'
    mast_text = "#101C33" if th["primary_is_light"] else "#FFFFFF"

    page = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)} — {esc(subtitle)}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Oswald:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
  :root{{
    --royal:{th["primary"]}; --field:{th["field"]}; --red:{th["secondary"]}; --red-dk:{th["sec_dark"]}; --red-tx:{th["sec_text"]};
    --chalk:#FFFFFF; --ice:{th["ice"]}; --ice-line:{th["ice_line"]}; --red-wash:{th["sec_wash"]}; --red-line:{th["sec_line"]};
    --slate:#5A6B85; --ink:#101C33; --gold:{th["accent"]}; --ladder:{th["ladder_text"]}; --ladder-sub:{th["ladder_sub"]}; --mast-text:{mast_text};
    --disp:"Oswald","Arial Narrow","Helvetica Neue Condensed",Impact,sans-serif;
    --body:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;
  }}
  *{{box-sizing:border-box}} html{{-webkit-text-size-adjust:100%}}
  body{{margin:0;background:var(--chalk);color:var(--ink);font-family:var(--body);font-size:15px;line-height:1.5;padding-bottom:56px}}
  .wrap{{max-width:760px;margin:0 auto}}
  .mast{{background:var(--royal);color:var(--mast-text);padding:20px 18px 16px}}
  .mast .club{{font-family:var(--disp);font-weight:700;font-size:30px;line-height:.98;letter-spacing:-.01em;margin:0}}
  .mast .club span{{display:block;color:var(--gold);font-size:15px;font-weight:500;letter-spacing:.06em;margin-top:6px}}
  .meta{{display:flex;flex-wrap:wrap;gap:6px;margin-top:14px}}
  .chip{{background:rgba(255,255,255,.13);border:1px solid rgba(255,255,255,.28);border-radius:2px;padding:3px 8px;font-size:12.5px}}
  .stripe{{height:5px;background:var(--red)}}
  .ladder{{position:sticky;top:0;z-index:40;background:var(--field);border-bottom:3px solid var(--red);display:flex;overflow-x:auto;scrollbar-width:none}}
  .ladder::-webkit-scrollbar{{display:none}}
  .ladder a{{flex:0 0 auto;color:var(--ladder);text-decoration:none;font-family:var(--disp);font-weight:600;font-size:19px;padding:9px 14px;border-right:1px solid rgba(255,255,255,.12)}}
  .ladder a small{{display:block;font-family:var(--body);font-size:9.5px;font-weight:600;letter-spacing:.09em;color:var(--ladder-sub)}}
  .ladder a:hover,.ladder a:focus{{background:var(--red);color:#fff}} .ladder a:hover small,.ladder a:focus small{{color:#fff}}
  section{{padding:22px 18px 4px}}
  h2{{font-family:var(--disp);font-weight:700;font-size:23px;margin:0 0 3px;color:var(--royal)}}
  h2 + .sub{{color:var(--slate);font-size:13.5px;margin:0 0 16px;max-width:62ch}}
  h3{{font-family:var(--disp);font-weight:600;font-size:17px;margin:22px 0 8px;color:var(--ink)}}
  .rule{{margin:18px;border:2px solid var(--red);border-radius:3px;overflow:hidden}}
  .rule .hd{{background:var(--red);color:#fff;padding:8px 14px;font-family:var(--disp);font-weight:600;font-size:16px}}
  .rule .bd{{padding:14px}}
  .repl{{display:flex;gap:10px;margin:0 0 12px}}
  .repl div{{flex:1;text-align:center;background:var(--ice);border:1px solid var(--ice-line);border-radius:3px;padding:9px 4px}}
  .repl b{{display:block;font-family:var(--disp);font-size:27px;font-weight:700;color:var(--royal);line-height:1}}
  .repl s{{display:block;text-decoration:none;font-size:11px;color:var(--slate);margin-top:3px}}
  .repl .hot b{{color:var(--red-tx)}}
  .rule p{{margin:0 0 9px;font-size:14px}} .rule p:last-child{{margin-bottom:0}}
  .howto{{background:var(--ice);border-top:1px solid var(--ice-line);border-bottom:1px solid var(--ice-line);padding:14px 18px}}
  .howto dl{{margin:0;display:grid;grid-template-columns:auto 1fr;gap:5px 12px;font-size:13.5px}}
  .howto dt{{font-weight:700;color:var(--royal);white-space:nowrap}} .howto dd{{margin:0;color:#243654}}
  .pick{{border-top:1px solid var(--ice-line);padding:0 0 6px}} .pick:first-of-type{{border-top:none}}
  .pickhd{{display:flex;align-items:stretch}}
  .jersey{{flex:0 0 84px;background:var(--royal);color:var(--mast-text);text-align:center;padding:9px 0 8px;border-bottom:4px solid var(--red)}}
  .jersey b{{display:block;font-family:var(--disp);font-weight:700;font-size:38px;line-height:.9;letter-spacing:-.02em}}
  .jersey s{{display:block;text-decoration:none;font-size:10px;font-weight:700;letter-spacing:.1em;opacity:.75;margin-top:2px}}
  .picknote{{flex:1;padding:10px 14px;background:var(--ice);border-bottom:1px solid var(--ice-line);font-size:13.5px;color:#1B2C4A;display:flex;align-items:center}}
  table{{width:100%;border-collapse:collapse;font-size:14px}}
  thead th{{text-align:left;font-size:10.5px;font-weight:700;letter-spacing:.07em;color:var(--slate);padding:7px 6px 5px;border-bottom:1px solid var(--ice-line)}}
  thead th.n{{text-align:right}}
  tbody td{{padding:8px 6px;border-bottom:1px solid #EDF1F8;vertical-align:middle}} tbody td.n{{text-align:right;font-variant-numeric:tabular-nums}}
  tbody tr{{cursor:pointer;-webkit-tap-highlight-color:transparent}} tbody tr:hover{{background:#F7FAFF}}
  .nm{{font-weight:600}}
  .pos{{display:inline-block;min-width:26px;text-align:center;font-size:10px;font-weight:700;letter-spacing:.05em;padding:2px 4px;border-radius:2px;margin-right:7px;color:#fff}}
  .pos.RB{{background:var(--red-tx)}} .pos.WR{{background:var(--royal)}} .pos.TE{{background:#0E7C6B}} .pos.QB{{background:#5B3E9E}} .pos.K,.pos.DEF{{background:var(--slate)}}
  .sur{{font-family:var(--disp);font-weight:600;font-size:16px}}
  .s-elite{{color:var(--red-tx)}} .s-good{{color:var(--royal)}} .s-ok{{color:#38507A}} .s-meh{{color:#93A2BA}}
  .bar{{position:relative;height:6px;background:#E4EBF6;border-radius:3px;min-width:52px;display:block}}
  .bar i{{position:absolute;inset:0 auto 0 0;background:var(--royal);border-radius:3px}} .bar.lo i{{background:var(--red-tx)}}
  .pct{{font-size:11px;color:var(--slate);display:block;margin-top:2px;font-variant-numeric:tabular-nums}}
  tr.gone{{opacity:.34}} tr.gone .nm{{text-decoration:line-through}}
  .tier{{border:1px solid var(--ice-line);border-radius:3px;margin:0 0 20px;overflow:hidden}}
  .tier > .th{{background:var(--field);color:#fff;padding:8px 12px;font-family:var(--disp);font-weight:600;font-size:16px;display:flex;justify-content:space-between;align-items:baseline}}
  .tier > .th em{{font-family:var(--body);font-style:normal;font-size:11.5px;color:var(--ladder);font-weight:400}}
  .band{{padding:4px 12px 2px}}
  .bandhd{{font-size:11px;font-weight:700;letter-spacing:.06em;color:var(--royal);padding:8px 0 3px;text-transform:uppercase}}
  .bandhd span{{color:var(--slate);font-weight:600;letter-spacing:0;text-transform:none;font-size:11.5px}}
  .cliff{{display:flex;align-items:center;gap:9px;margin:8px -12px;padding:5px 12px;background:var(--red-wash);border-top:2px solid var(--red);border-bottom:1px solid var(--red-line)}}
  .cliff b{{font-family:var(--disp);font-size:15px;color:var(--red-tx)}} .cliff span{{font-size:12px;color:var(--red-tx)}}
  .plist{{margin:0;padding:0;list-style:none}}
  .plist li{{display:flex;align-items:baseline;gap:8px;padding:4px 0;border-bottom:1px solid #F1F5FB;font-size:13.5px;cursor:pointer}}
  .plist li:last-child{{border-bottom:none}} .plist li.gone{{opacity:.34;text-decoration:line-through}}
  .plist .pn{{flex:1;font-weight:600}} .plist .pa{{color:var(--slate);font-size:11.5px;font-variant-numeric:tabular-nums;white-space:nowrap}}
  .plist .pp{{font-family:var(--disp);font-weight:600;font-variant-numeric:tabular-nums;white-space:nowrap}}
  .mine{{background:#FFF8E1;box-shadow:inset 3px 0 0 var(--gold);padding-left:7px!important;margin-left:-7px}}
  .verd td:last-child{{font-weight:600;white-space:nowrap}}
  .tag{{display:inline-block;padding:2px 7px;border-radius:2px;font-size:11px;font-weight:700;letter-spacing:.04em;color:#fff}}
  .tag.take{{background:#0E7C6B}} .tag.ok{{background:var(--royal)}} .tag.pass{{background:var(--red-tx)}}
  .vg{{margin:0;padding:0;list-style:none}}
  .vg li{{display:grid;grid-template-columns:78px 1fr;gap:10px;padding:9px 0;border-bottom:1px solid #EDF1F8;font-size:13.5px}}
  .vg b{{font-family:var(--disp);font-weight:600;font-size:15px;color:var(--royal);line-height:1.2}}
  .roster{{border:2px solid var(--royal);border-radius:3px;overflow:hidden;margin-bottom:6px}}
  .roster .rh{{background:var(--royal);color:var(--mast-text);padding:9px 13px;font-family:var(--disp);font-size:16px;font-weight:600;display:flex;justify-content:space-between}}
  .roster table{{font-size:13.5px}} .roster tbody td{{padding:7px 12px}} .roster tbody tr{{cursor:default}}
  .roster .rd{{font-family:var(--disp);font-weight:600;color:var(--slate);width:46px}}
  .appx{{background:var(--field);color:#DCE6F7;padding-bottom:34px}}
  .appx h2{{color:#fff}} .appx h2 + .sub{{color:var(--ladder)}}
  .appx h3{{color:var(--gold);border-bottom:1px solid rgba(255,255,255,.16);padding-bottom:5px}}
  .appx dl{{display:grid;grid-template-columns:1fr;gap:12px;margin:0}}
  .appx dt{{font-weight:700;color:#fff;font-size:14px}} .appx dd{{margin:2px 0 0;font-size:13.5px;color:#C6D5EE}}
  .appx ul{{margin:8px 0 0;padding-left:20px;font-size:13.5px;color:#C6D5EE}} .appx li{{margin-bottom:7px}}
  .appx .warn{{border-left:3px solid var(--red);padding:2px 0 2px 12px;margin:14px 0;color:#F3C9D2;font-size:13.5px}}
  .appx code{{background:rgba(255,255,255,.1);padding:1px 5px;border-radius:2px;font-size:12.5px}}
  .tools{{position:fixed;bottom:0;left:0;right:0;z-index:50;background:var(--field);border-top:3px solid var(--red);display:flex;align-items:center;gap:10px;padding:8px 14px;color:#fff;font-size:12.5px}}
  .tools .ct{{flex:1;color:var(--ladder)}} .tools .ct b{{color:#fff;font-family:var(--disp);font-size:16px}}
  .tools button{{font:inherit;font-weight:600;background:transparent;color:#fff;border:1px solid rgba(255,255,255,.4);border-radius:2px;padding:5px 11px;cursor:pointer}}
  .tools button:hover{{background:var(--red);border-color:var(--red)}}
  .credit{{text-align:center;font-size:11.5px;color:var(--slate);padding:14px 18px 24px}} .credit a{{color:var(--royal)}}
  @media (min-width:620px){{.mast .club{{font-size:40px}} .appx dl{{grid-template-columns:1fr 1fr;gap:14px 26px}}}}
  @media print{{
    .ladder,.tools{{display:none}} body{{padding-bottom:0;font-size:10.5pt}} .wrap{{max-width:none}}
    *{{-webkit-print-color-adjust:exact;print-color-adjust:exact}}
    .pagebreak{{break-before:page;page-break-before:always}} .tier,.pick,.roster,.rule{{break-inside:avoid;page-break-inside:avoid}}
  }}
</style>
</head>
<body>
<div class="wrap">
  <header class="mast">
    <h1 class="club">{esc(title)}<span>{esc(subtitle)}</span></h1>
    <div class="meta">{chips}</div>
  </header>
  <div class="stripe"></div>
  <nav class="ladder" aria-label="Jump to a pick">{ladder_links}</nav>

  <div class="rule">
    <div class="hd">{esc(hr.get("heading", "The only number you need to remember"))}</div>
    <div class="bd">
      <div class="repl">
        <div class="hot"><b>{esc(hot.get("value", repl.get("RB", "")))}</b><s>{esc(hot.get("label", "worst RB you'll ever have to start"))}</s></div>
        <div><b>{esc(cool.get("value", repl.get("WR", "")))}</b><s>{esc(cool.get("label", "worst WR you'll ever have to start"))}</s></div>
      </div>
      {hr_paras}
    </div>
  </div>

  <div class="howto">
    <dl>
      <dt>Proj</dt><dd>Points this player scores over the whole season in your exact scoring.</dd>
      <dt>Surplus</dt><dd>Proj minus the replacement number above. <b>This is the column that decides your pick.</b></dd>
      <dt>There</dt><dd>How often he's still on the board at that pick, out of {sim["settings"]["sims"]:,} simulated drafts.</dd>
      <dt>Tap</dt><dd>Tap any player to cross him off when someone else drafts him.</dd>
    </dl>
  </div>

  <section>
    <h2>Your picks, in order</h2>
    <p class="sub">Top {args.top} at each turn, ranked by surplus. The note beside the pick number is the decision.</p>
    {"".join(blocks)}
    {late_block}
  </section>

  <section id="tiers" class="pagebreak">
    <h2>Tier boards</h2>
    <p class="sub">Grouped by real scoring gaps, not by round. A colored bar is a cliff — the point drop between the man above it and the man below. Gold marks a player you already own or are targeting.</p>
    {"".join(tier_html)}
  </section>

  <section id="names" class="pagebreak">
    <h2>Your shortlist, scored</h2>
    <p class="sub">{esc(notes.get("shortlist_sub", "The names you flagged, run through the same surplus math."))}</p>
    <table class="verd">
      <thead><tr><th>Player</th><th class="n">Proj</th><th class="n">Surplus</th><th>Call</th></tr></thead>
      <tbody>{"".join(sl)}</tbody>
    </table>
    {"<h3>What the betting market thinks</h3><ul class='vg'>" + vg + "</ul>" if vg else ""}
    <h3>The roster to aim for</h3>
    <div class="roster">
      <div class="rh"><span>Target build</span><span>{esc(tb.get("total", ""))} projected</span></div>
      <table><tbody>{"".join(tb_rows)}</tbody></table>
    </div>
    <p class="sub" style="margin-top:10px">{esc(notes.get("target_note", ""))}</p>
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
  <p class="credit">Built with <a href="https://github.com/{esc((notes.get("repo") or (notes.get("appendix") or {}).get("repo") or "nicoandmelissa/fantasy-draft-analyst"))}">fantasy-draft-analyst</a> — free and open source.</p>
</div>

<div class="tools">
  <span class="ct"><b id="cnt">0</b> crossed off</span>
  <button type="button" id="rst">Reset</button>
  <button type="button" id="prt">Print</button>
</div>

<script>
(function(){{
  var gone = new Set(); var cnt = document.getElementById('cnt');
  function nameOf(el){{ var n = el.querySelector('.nm') || el.querySelector('.pn'); return n ? n.textContent.replace(/\\s*—\\s*yours\\s*$/,'').trim() : null; }}
  function paint(){{ document.querySelectorAll('tbody tr, .plist li').forEach(function(el){{ var nm = nameOf(el); if(!nm) return; el.classList.toggle('gone', gone.has(nm)); el.setAttribute('aria-pressed', gone.has(nm) ? 'true' : 'false'); }}); cnt.textContent = gone.size; }}
  function toggle(el){{ var nm = nameOf(el); if(!nm) return; if(gone.has(nm)) gone.delete(nm); else gone.add(nm); paint(); }}
  document.querySelectorAll('tbody tr, .plist li').forEach(function(el){{
    if(!nameOf(el)) return; if(el.closest('.roster')) return;
    el.setAttribute('tabindex','0'); el.setAttribute('role','button');
    el.addEventListener('click', function(){{ toggle(el); }});
    el.addEventListener('keydown', function(e){{ if(e.key === 'Enter' || e.key === ' '){{ e.preventDefault(); toggle(el); }} }});
  }});
  document.getElementById('rst').addEventListener('click', function(){{ gone.clear(); paint(); }});
  document.getElementById('prt').addEventListener('click', function(){{ window.print(); }});
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
