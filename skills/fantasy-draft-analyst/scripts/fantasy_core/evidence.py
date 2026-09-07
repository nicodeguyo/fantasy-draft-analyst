"""Validate dated stat-line evidence, re-score, then blend independent groups.

No network on the draft-clock path. Reports retain rejected records and reasons.
A projection mean is a transparent baseline, not a trained forecasting model.
"""
from datetime import datetime, timezone, timedelta
from statistics import mean, pstdev
import math
from .identity import IdentityIndex
from .news import timestamp, ledger, apply_adjustments
from scoring import score_row

COMMON = {'rush_yd', 'rush_td', 'rec', 'rec_yd', 'rec_td', 'fum', 'two_pt'}
REQUIRED = {'QB': COMMON | {'pass_yd', 'pass_td', 'int'}, 'RB': COMMON,
            'WR': COMMON, 'TE': COMMON, 'K': {'fg', 'fg_miss', 'xp'},
            'DEF': {'sacks', 'def_int', 'fum_rec', 'def_td', 'safety', 'pts_allowed'}}


def number(value, field):
    if value is None or isinstance(value, bool) or str(value).strip() in ('', '-', '—'):
        raise ValueError('Missing numeric field: ' + field)
    try:
        v = float(str(value).replace(',', ''))
    except (ValueError, TypeError):
        raise ValueError('Malformed numeric field: ' + field) from None
    if not math.isfinite(v):
        raise ValueError('Nonfinite numeric field: ' + field)
    return v


def validate_projection(record, player, snapshot, now, max_age_days):
    for field in ('source', 'independence_group', 'url', 'fetched_at', 'season', 'period'):
        if not record.get(field):
            raise ValueError('Missing projection metadata: ' + field)
    for field in ('season', 'period', 'week'):
        if record.get(field) != snapshot.get(field):
            raise ValueError('Projection ' + field + ' does not match snapshot')
    fetched = timestamp(record['fetched_at'])
    if fetched > now:
        raise ValueError('Projection was fetched after analysis time')
    if record.get('projection_convention', 'season_total') != 'season_total':
        raise ValueError('Provider stat line must be normalized to season_total before blending')
    warnings = []
    updated = record.get('updated_at')
    if updated:
        observed = timestamp(updated)
        if observed > fetched:
            raise ValueError('Source update is after fetch time')
        if now - observed > timedelta(days=max_age_days):
            raise ValueError('Stale projection source update')
    else:
        warnings.append('Source update time unknown; fetch time is not content freshness')
        if now - fetched > timedelta(days=max_age_days):
            raise ValueError('Stale cached projection, source update unknown')
    if record.get('independence_verified') is not True:
        warnings.append('Source independence is unverified; do not claim independent consensus')
    stats = {key: number(value, key) for key, value in record.get('stats', {}).items()}
    assumptions = record.get('assumed_zeros', {})
    structural = set(record.get('structural_zeros', []))
    # Applicable stats cannot be called structurally inapplicable (e.g. RB receiving).
    if structural & REQUIRED[player['pos']]:
        raise ValueError('Applicable stats cannot be structural zeros')
    for key in structural:
        if key in stats and stats[key] != 0:
            raise ValueError('Structural zero conflicts with observed stat: ' + key)
        stats[key] = 0.0
    for key, reason in assumptions.items():
        if not reason or key in stats:
            raise ValueError('Zero assumption needs reason and must not overwrite supplied stat')
        stats[key] = 0.0
        warnings.append('Assumed zero for ' + key + ': ' + str(reason))
    missing = REQUIRED[player['pos']] - stats.keys()
    if missing:
        raise ValueError('Missing applicable projection stats: ' + ', '.join(sorted(missing)))
    return stats, warnings


def prepare_snapshot(snapshot, league, now=None, max_age_days=3):
    if snapshot.get('schema_version') != 1:
        raise ValueError('Unsupported evidence schema_version; expected 1')
    if snapshot.get('period') not in ('season', 'week', 'rest_of_season'):
        raise ValueError('Explicit season/week/rest_of_season period required')
    if not isinstance(snapshot.get('season'), int):
        raise ValueError('Integer season required')
    if snapshot['period'] == 'week' and not isinstance(snapshot.get('week'), int):
        raise ValueError('Weekly evidence requires week')
    if snapshot['period'] != 'week' and snapshot.get('week') is not None:
        raise ValueError('Only weekly evidence can specify week')
    league_meta = league.get('league') or {}
    for season in (league.get('season'), league_meta.get('season')):
        if season is not None and season != snapshot['season']:
            raise ValueError('League season differs from snapshot')
    formats = {value for value in (league.get('draft_format'), league_meta.get('draft_format')) if value}
    if len(formats) > 1:
        raise ValueError('Conflicting root and nested draft_format')
    draft_format = next(iter(formats), 'managed-1qb')
    now = timestamp(now) if isinstance(now, str) else (now or datetime.now(timezone.utc))
    if max_age_days <= 0:
        raise ValueError('max_age_days must be positive')
    IdentityIndex(snapshot.get('players', []))
    rows, details, warnings = [], [], []
    scoring = league.get('scoring', {})
    supported_scoring = {'pass_yard','pass_td','interception','rush_yard','rush_td','reception','te_premium',
                         'rec_yard','rec_td','fumble_lost','two_point','bonuses','fg','fg_miss','xp','sack',
                         'def_int','fum_rec','def_td','safety'}
    if set(scoring) - supported_scoring:
        raise ValueError('Unsupported scoring keys: ' + ', '.join(sorted(set(scoring) - supported_scoring)))
    for key, value in scoring.items():
        if key != 'bonuses':
            number(value, 'scoring.' + key)
    if scoring.get('bonuses'):
        raise ValueError('Per-game bonuses require game-level forecasts; season approximation is not accepted by evidence preparation')
    known_ids = {player['player_id'] for player in snapshot.get('players', [])}
    unknown_news = [event for event in snapshot.get('news', []) if event.get('player_id') not in known_ids]
    news = ledger([event for event in snapshot.get('news', []) if event.get('player_id') in known_ids], now.isoformat())
    news['quarantined'] = unknown_news
    if unknown_news:
        news['warnings'].append(str(len(unknown_news)) + ' news records have unresolved player identity')
    context = validate_context(snapshot, now, max_age_days)
    warnings.extend(context['warnings'])
    for player in snapshot.get('players', []):
        detail = {'player_id': player['player_id'], 'name': player.get('name'), 'accepted': [], 'rejected': [], 'warnings': []}
        details.append(detail)
        if player.get('pos') not in REQUIRED or not player.get('name'):
            detail['rejected'].append({'reason': 'Unknown position or missing name'})
            continue
        groups = {}
        group_verified = {}
        seen_sources = set()
        for record in player.get('projections', []):
            try:
                if record.get('source') in seen_sources:
                    raise ValueError('Duplicate source projection; resolve the source revision explicitly')
                seen_sources.add(record.get('source'))
                stats, record_warnings = validate_projection(record, player, snapshot, now, max_age_days)
                pts = score_row(dict(stats, pos=player['pos']), scoring)
                if player['pos'] in ('K', 'DEF'):
                    record_warnings.append('K/DEF scoring uses aggregate approximations; verify league distance/bucket rules')
                scored = dict(record, league_points=pts, warnings=record_warnings)
                detail['accepted'].append(scored)
                groups.setdefault(record['independence_group'], []).append(pts)
                group_verified[record['independence_group']] = group_verified.get(record['independence_group'], True) and record.get('independence_verified', False)
                detail['warnings'].extend(record_warnings)
            except (ValueError, TypeError, KeyError) as exc:
                detail['rejected'].append({'record': record, 'reason': str(exc)})
        # Merge sources with overlapping known constituents rather than counting
        # a consensus and one of its publishers as independent votes.
        publishers = {}
        for record in detail['accepted']:
            group = record['independence_group']
            publishers.setdefault(group, set()).update(record.get('constituents') or [group])
        changed = True
        while changed:
            changed = False
            keys = list(groups)
            for i, left in enumerate(keys):
                for right in keys[i+1:]:
                    if publishers[left] & publishers[right]:
                        groups[left].extend(groups.pop(right))
                        publishers[left].update(publishers.pop(right))
                        group_verified[left] = group_verified[left] and group_verified.pop(right)
                        changed = True
                        break
                if changed:
                    break
        values = [mean(points) for points in groups.values()]
        verified_groups = sum(bool(v) for v in group_verified.values())
        mode = 'full' if verified_groups >= 2 and not detail['warnings'] else 'limited' if values else 'rank-only'
        if detail['rejected'] and mode == 'full':
            mode = 'limited'
        detail['mode'] = mode
        detail['verified_independent_sources'] = verified_groups
        detail['group_points'] = {group: mean(points) for group, points in groups.items()}
        if not values:
            continue
        points = mean(values)
        known_events = {event['event_id'] for event in news['active'] if event['player_id'] == player['player_id']}
        for adjustment in player.get('adjustments', []):
            if adjustment.get('event_id') not in known_events:
                raise ValueError('Adjustment references unknown, superseded or other-player event')
        points, adjustments = apply_adjustments(points, player.get('adjustments', []), detail['accepted'])
        detail['adjustments'] = adjustments
        detail['projection_sd'] = pstdev(values) if len(values) > 1 else None
        detail['league_points'] = round(points, 1)
        price = player.get('adp', {})
        try:
            if price.get('season') != snapshot['season'] or price.get('kind', 'adp') != 'adp':
                raise ValueError('Missing/current-season ADP required; ranks are not ADP')
            if price.get('format') != draft_format:
                raise ValueError('ADP format differs from league draft_format')
            if not price.get('source') or not price.get('updated_at'):
                raise ValueError('ADP needs source and update timestamp')
            price_time = timestamp(price['updated_at'])
            if price_time > now or now-price_time > timedelta(days=max_age_days):
                raise ValueError('ADP stale or from future')
            adp = number(price.get('value'), 'adp')
            if adp <= 0:
                raise ValueError('ADP must be positive')
            sd = price.get('sd')
            if sd is not None:
                sd = number(sd, 'adp_sd')
                if sd < 0:
                    raise ValueError('ADP standard deviation cannot be negative')
            else:
                detail['warnings'].append('ADP spread unavailable; engine may use an explicitly assumed price spread')
            detail['expected_games_by_source'] = {record['source']:record.get('expected_games') for record in detail['accepted']}
            if player.get('expected_games') is None:
                detail['warnings'].append('Player expected games not established; provider conventions retained without assuming 17 games')
            else:
                games = number(player['expected_games'], 'expected_games')
                if not 0 <= games <= 18:
                    raise ValueError('Expected games must be between 0 and 18')
                if games == 0 and points != 0:
                    raise ValueError('Zero expected games contradicts nonzero season-total points')
            if player.get('performance_sd') is not None:
                if number(player['performance_sd'], 'performance_sd') < 0:
                    raise ValueError('Performance standard deviation cannot be negative')
            if detail['warnings']:
                mode = 'limited'
                detail['mode'] = mode
            rows.append({'player_id': player['player_id'], 'name': player['name'], 'pos': player['pos'], 'team': player.get('team', ''),
                         'adp': adp, 'adp_sd': '' if sd is None else sd, 'proj': round(points, 1), 'bye': player.get('bye', ''),
                         'projection_sd': detail['projection_sd'] if detail['projection_sd'] is not None else '',
                         'source_count': len(detail['accepted']), 'independent_sources': verified_groups, 'evidence_mode': mode,
                         'expected_games': player.get('expected_games', ''), 'projection_convention': 'season_total',
                         'performance_sd': player.get('performance_sd', ''),
                         'note': '; '.join(dict.fromkeys(detail['warnings']))})
        except (ValueError, TypeError) as exc:
            detail['warnings'].append(str(exc))
    # Snapshot health includes uncovered players; two good rows cannot hide a partial feed.
    mode = 'full' if rows and len(rows) == len(details) and all(d.get('mode') == 'full' for d in details) else 'limited' if rows else 'rank-only'
    if snapshot['period'] != 'season':
        warnings.append('Not full-season data: this snapshot is not eligible for the season draft engine')
    if mode == 'rank-only':
        warnings.append('No eligible projection+price rows; no point differences or availability probabilities may be reported')
    report = {'schema_version': 1, 'as_of': now.isoformat(), 'season': snapshot['season'], 'period': snapshot['period'],
              'mode': mode, 'engine_eligible': bool(rows) and snapshot['period'] == 'season',
              'warnings': warnings + news['warnings'], 'players': details, 'news': news,
              'context': context, 'input_snapshot': snapshot}
    return sorted(rows, key=lambda r: r['adp']), report


def validate_context(snapshot, now, max_age_days):
    """Usage denominators and market lines remain evidence, never point bonuses."""
    accepted = {'usage': [], 'markets': []}
    rejected, warnings = [], []
    known_ids = {player['player_id'] for player in snapshot.get('players', [])}
    for kind in accepted:
        for record in snapshot.get(kind, []):
            try:
                required = ('source','url','season','observed_at') if kind == 'usage' else ('book','url','season','observed_at','kind','line')
                if any(record.get(field) is None or record.get(field) == '' for field in required):
                    raise ValueError('Missing context source/date/measurement')
                if record['season'] > snapshot['season']:
                    raise ValueError('Future-season evidence')
                observed = timestamp(record['observed_at'])
                if observed > now:
                    raise ValueError('Context observed after analysis time')
                if record.get('player_id') is not None and record['player_id'] not in known_ids:
                    raise ValueError('Context player identity is unresolved')
                if kind == 'usage':
                    if not record.get('metric') or not record.get('player_id'):
                        raise ValueError('Usage requires player_id and metric')
                    number(record.get('value'), 'usage.value')
                    if not record.get('sample'):
                        raise ValueError('Usage requires season/weeks/games sample description')
                    if any(word in record['metric'] for word in ('share','rate','per_route','participation')):
                        if number(record.get('denominator'), 'usage.denominator') <= 0:
                            raise ValueError('Usage denominator must be positive')
                else:
                    if record['season'] != snapshot['season'] or record.get('period') not in ('season','week','rest_of_season'):
                        raise ValueError('Market must specify matching season and supported forecast period')
                    if record['period'] == 'week':
                        week = record.get('week')
                        if isinstance(week, bool) or not isinstance(week, int) or not 1 <= week <= 18:
                            raise ValueError('Weekly market requires week 1 through 18')
                    elif record.get('week') is not None:
                        raise ValueError('Only weekly market may specify week')
                    number(record['line'], 'market.line')
                    if not record.get('metric') or not record.get('unit'):
                        raise ValueError('Market requires metric and unit')
                    if not any(record.get(k) is not None for k in ('price','over_price','under_price')):
                        raise ValueError('Market requires quoted price as well as line')
                    for key in ('price','over_price','under_price'):
                        if record.get(key) is not None:
                            number(record[key], 'market.' + key)
                    if record['kind'] not in ('player_prop','team_total','win_total'):
                        raise ValueError('Unknown market kind')
                    if record['kind'] == 'player_prop' and not record.get('player_id'):
                        raise ValueError('Player prop requires canonical player identity')
                    if not record.get('player_id') and not record.get('team'):
                        raise ValueError('Market requires player or team identity')
                    if now-observed > timedelta(days=max_age_days):
                        raise ValueError('Stale market observation')
                accepted[kind].append(record)
            except (ValueError, TypeError) as exc:
                rejected.append({'kind':kind,'record':record,'reason':str(exc)})
    if rejected:
        warnings.append(str(len(rejected)) + ' context records quarantined; not used in advice')
    return dict(accepted, rejected=rejected, warnings=warnings)
