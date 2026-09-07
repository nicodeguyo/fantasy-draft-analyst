"""One static saved-board policy shared by the HTML and its internal benchmark.

The order includes collapsed rows. Notes can nominate a late target but never override
an evaluated plan_path target. All candidate estimates remain frozen before the draft.
"""
from collections import Counter

POLICY_VERSION = 'saved-board-v2'
POLICY_DESCRIPTION = ('Follow the first available eligible row, including the more rows. '
    'Skip avoid-list players and filled position caps (QB 2 plus superflex, RB 6, WR 7, TE 2, K 1, DEF 1). '
    'When remaining picks equal unfilled starting slots, choose only a player who fills one. '
    'If no row qualifies, use the fallback order below. Marking picks does not recalculate values.')


def row_groups(sim, notes, players, pk, top_n=5, matrix=None):
    """Return visible rows, collapsed rows and nominated target for one actual pick."""
    matrix = matrix or {}
    key = str(pk)
    pp = next((r for r in sim.get('plan_path', []) if str(r['pick']) == key), {})
    evaluated = {str(r['pick']) for r in sim.get('plan_path', [])}
    plans = {r['player']: str(r.get('pick', '')) for r in notes.get('plan', [])
             if r.get('player') and str(r.get('pick')) not in evaluated}
    for r in sim.get('plan_path', []):
        plans[r['player']] = str(r['pick'])
    target = pp.get('player') or next((n for n, p in plans.items() if p == key), None)
    note = (notes.get('pick_notes') or {}).get(key, '')
    prose = ' '.join(str(x) for x in note.values()) if isinstance(note, dict) else str(note)
    named = {n for n in players if n in prose} | {n for n, p in plans.items() if p == key}
    pv = (sim.get('pick_values') or {}).get(key)
    rows = [dict(r) for r in (pv or sim.get('availability', {}).get(key, []))]
    # Keep the whole saved ranking. Expanded rows are part of the delivered policy.
    rows.sort(key=lambda r: (r['name'] != target, -r.get('value', r.get('surplus', 0))))
    have = {r['name'] for r in rows}
    for name in sorted(named - have):
        p = players.get(name)
        if not p:
            continue
        proj = float(p.get('proj') or 0)
        rows.append({'name': name, 'pos': p['pos'], 'proj': round(proj),
                     'surplus': round(proj - sim['replacement'].get(p['pos'], 0)),
                     'there': matrix.get(name, {}).get(pk), 'watch': True})
    # Availability exports also contain watch/earlier-target reference rows at 0%.
    # Beyond rollouts, use the same 15% floor as the simulator's candidate table.
    # Apply after notes are merged so prose cannot reintroduce a known-gone player.
    if not pv:
        rows = [r for r in rows if r.get('there') is None or r['there'] >= 15]
        if target and not any(r['name'] == target for r in rows):
            target = None
    rows.sort(key=lambda r: (r['name'] != target, r.get('value') is None if pv else False,
                             -r.get('value', r.get('surplus', 0))))
    visible, hidden = rows[:top_n], rows[top_n:]
    promoted = [r for r in hidden if r['name'] in named]
    hidden = [r for r in hidden if r['name'] not in named]
    visible += promoted
    visible.sort(key=lambda r: (r['name'] != target, r.get('value') is None if pv else False,
                                -r.get('value', r.get('surplus', 0))))
    return visible, hidden, target


def fallback_order(sim, players):
    """All input players, ranked by projected surplus, then ADP and name."""
    return sorted(players, key=lambda n: (
        -(float(players[n].get('proj') or 0) - sim['replacement'].get(players[n]['pos'], 0)),
        float(players[n].get('adp') or 9999), n))


def filled_slots(roster, starters):
    counts = Counter(p['pos'] for p in roster)
    filled = 0
    for pos in ('QB', 'RB', 'WR', 'TE', 'K', 'DEF'):
        take = min(counts[pos], starters.get(pos, 0))
        counts[pos] -= take
        filled += take
    flex = min(sum(counts[p] for p in ('RB', 'WR', 'TE')), starters.get('FLEX', 0))
    filled += flex
    # All flex-eligible positions are also superflex eligible, so only the count matters.
    sf_pool = sum(counts[p] for p in ('QB', 'RB', 'WR', 'TE')) - flex
    return filled + min(sf_pool, starters.get('SUPERFLEX', 0))


def eligible_players(avail, roster, starters, caps, avoid, remaining_picks):
    """The same starter-completion guard applies to the board and ADP baseline."""
    counts = Counter(p['pos'] for p in roster)
    filled = filled_slots(roster, starters)
    missing = sum(starters.get(p, 0) for p in ('QB', 'RB', 'WR', 'TE', 'K', 'DEF', 'FLEX', 'SUPERFLEX')) - filled
    return [p for p in avail if p['name'] not in avoid and counts[p['pos']] < caps[p['pos']]
            and (remaining_picks > missing or filled_slots(roster + [p], starters) > filled)]


def choose_player(names, fallback, avail, roster, starters, caps, avoid, remaining_picks):
    """Execute exactly the roster eligibility and ranking rule printed on the board."""
    candidates = {p['name']: p for p in eligible_players(avail, roster, starters, caps, avoid, remaining_picks)}
    for name in list(names) + list(fallback):
        if name in candidates:
            return candidates[name]
    raise ValueError('No eligible saved-board choice remains; check pool, avoid list and roster settings.')


def run_board(simulator, seed, board, fallback, adp_baseline=False):
    """Opponents use the simulator; every own-seat decision uses the printed policy."""
    st = simulator.start(seed)
    own = list(st['my_overall'])
    for idx, overall in enumerate(own):
        simulator.play(st, stop_at=overall)
        ov, rnd, team = st['order'][st['i']]
        if ov != overall or team != simulator.slot:
            raise ValueError('Unexpected simulator draft order')
        if adp_baseline:
            eligible = eligible_players(st['avail'], st['rosters'][team], simulator.starters,
                                        simulator.maxc, simulator.avoid, len(own) - idx)
            if not eligible:
                raise ValueError('No eligible ADP-baseline choice remains')
            p = simulator.opp_pick(eligible, st['rosters'][team], rnd, st['rng'])
        else:
            p = choose_player(board.get(overall, []), fallback, st['avail'], st['rosters'][team],
                              simulator.starters, simulator.maxc, simulator.avoid, len(own) - idx)
        st['picks'].append((overall, rnd, p))
        st['rosters'][team].append(p)
        st['avail'].remove(p)
        st['i'] += 1
    simulator.play(st)
    total, lineup = simulator.lineup_pts(st['rosters'][simulator.slot])
    return st['picks'], st['rosters'][simulator.slot], total, lineup
