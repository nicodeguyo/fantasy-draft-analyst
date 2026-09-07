"""Transparent draft roster utility, not a forecast of wins or weekly outcomes.

Season projections already include missed games. Keep those totals intact and add
only reserves' improvement over waiver fallback in explicit absence scenarios.
All lineups use pre-game expected rates; never realized weekly outcomes.
"""
from __future__ import annotations

from collections import defaultdict
import math

POSITIONS = ('QB', 'RB', 'WR', 'TE', 'K', 'DEF')
SKILL = ('RB', 'WR', 'TE')


def identity(p):
    return str(p.get('player_id') or p['name'])


def lineup(roster, cfg, replacements=None, value_key='proj'):
    """Best legal lineup at supplied *expected* values; each identity appears once.

    Dedicated slots, then FLEX, then SUPERFLEX is optimal for these nested
    eligibility sets. Replacement entries are distinct hypothetical waiver adds.
    Returns (value, selected real players). No realized-score input is inferred.
    """
    r = cfg.get('roster', {})
    counts = {'QB': 1, 'RB': 2, 'WR': 2, 'TE': 1, 'K': 1, 'DEF': 1,
              'FLEX': 1, 'SUPERFLEX': 0}
    counts.update({k: int(r[k]) for k in counts if k in r})
    if any(n < 0 for n in counts.values()):
        raise ValueError('Starter counts must be nonnegative')
    seen, pool = set(), []
    for p in roster:
        pid = identity(p)
        if pid in seen:
            raise ValueError(f'Duplicate roster identity: {pid}')
        seen.add(pid)
        value = float(p[value_key])
        if not math.isfinite(value):
            raise ValueError('Lineup expected values must be finite')
        pool.append((value, pid, p))
    pool.sort(key=lambda x: (-x[0], x[1]))
    used, selected, total = set(), [], 0.0
    for slot in POSITIONS + ('FLEX', 'SUPERFLEX'):
        eligible = SKILL if slot == 'FLEX' else SKILL + ('QB',) if slot == 'SUPERFLEX' else (slot,)
        n = counts[slot]
        if not n:
            continue
        choices = [x for x in pool if x[1] not in used and x[2]['pos'] in eligible]
        floor = max(float(replacements.get(pos, 0)) for pos in eligible) if replacements is not None else None
        taken = 0
        for value, pid, p in choices[:n]:
            if floor is not None and value <= floor:
                break
            used.add(pid)
            total += value
            selected.append(p)
            taken += 1
        if floor is not None:
            total += (n - taken) * floor
    return total, selected


def _settings(cfg):
    settings = cfg.get('valuation', {}) or {}
    horizon = float(settings.get('horizon_games', cfg.get('league', {}).get('season_games', 17)))
    if not math.isfinite(horizon) or horizon <= 0:
        raise ValueError('valuation.horizon_games must be positive')
    missed = float(settings.get('assumed_missed_games', 1.0))
    pair_share = float(settings.get('overlap_share', .25))
    if not 0 <= missed < horizon or not 0 <= pair_share <= 1:
        raise ValueError('Invalid missed-games or overlap assumption')
    return settings, horizon, missed, pair_share


def roster_value(roster, cfg, replacements=None, fill_replacement=True):
    """Return a decomposed utility using baseline + usable coverage + upside.

    Coverage approximates absent-starter weeks, combining single absences with
    overlapping pairs. Each scenario solves a legal lineup, so a backup cannot
    occupy two slots at once. This is not a full injury simulation. Known byes
    within valuation.weeks are additional exact simultaneous-absence scenarios;
    their games are removed from the general absence budget to avoid counting
    them twice. Set assumed_missed_games explicitly for the intended horizon.

    expected_games conventions:
      season_total (default): proj is expected total, never discounted again.
      per_game: multiply proj by expected_games to establish the season total.
      full_season: proj assumes full health; multiply by expected_games/horizon.
    """
    settings, horizon, default_missed, overlap = _settings(cfg)
    normalized, rates, misses = [], {}, {}
    assumptions = set()
    for original in roster:
        p = dict(original)
        pid = identity(p)
        raw_games = p.get('expected_games')
        games = float(raw_games) if raw_games not in (None, '') else horizon - default_missed
        if not math.isfinite(games) or not 0 <= games <= horizon:
            raise ValueError(f'expected_games for {p["name"]} must be in [0, horizon_games]')
        if raw_games in (None, ''):
            assumptions.add(f'Unknown expected_games: assume {default_missed:g} missed games over {horizon:g}; sensitivity required.')
        convention = p.get('projection_convention') or 'season_total'
        if convention == 'per_game':
            p['proj'] = float(p['proj']) * games
        elif convention == 'full_season':
            p['proj'] = float(p['proj']) * games / horizon
        elif convention != 'season_total':
            raise ValueError(f'Unsupported projection_convention: {convention}')
        p['proj'] = float(p['proj'])
        if games == 0 and p['proj'] != 0:
            raise ValueError('Zero expected_games requires zero expected season points')
        normalized.append(p)
        rates[pid] = p['proj'] / games if games else 0.
        misses[pid] = horizon - games
    repl = dict(replacements or {})
    baseline, selected = lineup(normalized, cfg, repl if fill_replacement else None)
    selected_ids = {identity(p) for p in selected}
    backups = [p for p in normalized if identity(p) not in selected_ids]
    # A fresh waiver player covers an absent week; replacement totals use full horizon.
    waiver = settings.get('waiver_points')
    if waiver is None:
        waiver = repl
        assumptions.add('Waiver fallback uses positional replacement cutoff; override valuation.waiver_points for league-specific waiver depth.')
    else:
        waiver = {**repl, **waiver}
        assumptions.add('Waiver fallback uses explicit valuation.waiver_points season totals.')
    waiver_rates = {pos: float(v) / horizon for pos, v in waiver.items()}
    if not all(math.isfinite(v) for v in waiver_rates.values()):
        raise ValueError('Waiver values must be finite')
    rate_roster = [dict(p, _rate=rates[identity(p)]) for p in normalized]
    core = [p for p in rate_roster if identity(p) in selected_ids]
    scenarios = []
    weeks = settings.get('weeks') or []
    for week in weeks:
        absent = {identity(p) for p in selected if str(p.get('bye', '')) == str(week)}
        if absent:
            scenarios.append((absent, 1.0, week))
            for pid in absent:
                misses[pid] = max(0., misses[pid] - 1.)
    # A deterministic ring samples overlapping absences in O(starters), keeping
    # live latency bounded. This is a coverage stress test, not learned injury correlation.
    starters = sorted(selected_ids)
    pair_budget = defaultdict(float)
    pairs = [(starters[0], starters[1])] if len(starters) == 2 else (
        [(starters[i], starters[(i + 1) % len(starters)]) for i in range(len(starters))]
        if len(starters) > 2 else [])
    for a, b in pairs:
        weight = overlap * min(misses[a], misses[b]) / (1 if len(starters) == 2 else 2)
        if weight:
            scenarios.append(({a, b}, weight, None))
            pair_budget[a] += weight
            pair_budget[b] += weight
    for pid in sorted(starters):
        weight = max(0., misses[pid] - pair_budget[pid])
        if weight:
            scenarios.append(({pid}, weight, None))
    coverage = 0.
    if backups:
        for absent, weight, exact_bye in scenarios:
            # Bench players on a known shared bye also cannot provide coverage.
            def available(p):
                return identity(p) not in absent and (exact_bye is None or str(p.get('bye', '')) != str(exact_bye))
            full = lineup([p for p in rate_roster if available(p)], cfg, waiver_rates, '_rate')[0]
            bare = lineup([p for p in core if available(p)], cfg, waiver_rates, '_rate')[0]
            coverage += weight * max(0., full - bare)
    # Explicit outcome-uncertainty inputs only. Source disagreement or ADP spread
    # is not a substitute for a football performance distribution.
    upside = 0.
    upside_weight = float(settings.get('upside_weight', .10))
    if not 0 <= upside_weight <= 1:
        raise ValueError('valuation.upside_weight must be between zero and one')
    if backups and upside_weight:
        bumped = []
        for p in normalized:
            sigma = 0. if p.get('expected_games') in (0, '0', '0.0') else float(p.get('performance_sd') or 0.)
            if not math.isfinite(sigma) or sigma < 0:
                raise ValueError('performance_sd must be finite and nonnegative')
            bumped.append(dict(p, proj=p['proj'] + (sigma if identity(p) not in selected_ids else 0)))
        upside = upside_weight * max(0., lineup(bumped, cfg, repl if fill_replacement else None)[0] - baseline)
    assumptions.add('Coverage is an absence-scenario utility increment over waiver fallback, not a win or expected-total forecast.')
    assumptions.add('Expected season totals are not discounted again; rate estimates divide totals by expected_games.')
    assumptions.add('Reserves assumed available outside known byes; overlapping injuries use a deterministic stress-test sample, not learned correlations.')
    assumptions.add('Unknown outcome variance receives no upside bonus; ADP spread and source disagreement are not performance variance.')
    return {'policy': 'roster_v2', 'total': baseline + coverage + upside,
            'starter_points': baseline, 'coverage_points': coverage, 'upside_points': upside,
            'starters': [identity(p) for p in selected], 'horizon_games': horizon,
            'assumptions': sorted(assumptions), 'scenario_count': len(scenarios)}
