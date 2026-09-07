"""As-of event ledger. Syndication is not independent corroboration."""
from datetime import datetime, timezone


def timestamp(value):
    if not isinstance(value, str):
        raise ValueError('An explicit ISO-8601 timestamp is required')
    dt = datetime.fromisoformat(value.replace('Z', '+00:00'))
    if dt.tzinfo is None:
        raise ValueError('Timestamp must include timezone: ' + value)
    return dt.astimezone(timezone.utc)


def ledger(events, as_of):
    now = timestamp(as_of)
    by_id, issues, scheduled = {}, [], []
    for event in events:
        required = ('event_id', 'player_id', 'type', 'original_source', 'url', 'event_at', 'published_at', 'quality')
        if any(not event.get(k) for k in required):
            raise ValueError('News event lacks required identity, source or date fields')
        if event['quality'] not in ('confirmed', 'reported', 'speculative'):
            raise ValueError('Unsupported news evidence quality')
        event_time = timestamp(event['event_at'])
        effective_time = timestamp(event['effective_at']) if event.get('effective_at') else event_time
        if timestamp(event['published_at']) > now:
            continue  # preserve raw input elsewhere; not knowable in this analysis
        if event_time > now or effective_time > now:
            scheduled.append(event)
            issues.append('Scheduled future event retained as context, not a completed status change: ' + event['event_id'])
            continue
        previous = by_id.get(event['event_id'])
        if previous and previous != event:
            raise ValueError('Conflicting duplicate event_id: ' + event['event_id'])
        by_id[event['event_id']] = event
    inactive = set()
    quality = {'speculative': 0, 'reported': 1, 'confirmed': 2}
    for event in by_id.values():
        if event.get('expires_at') and timestamp(event['expires_at']) <= now:
            inactive.add(event['event_id'])
        for old_id in event.get('supersedes', []):
            old = by_id.get(old_id)
            if not old or old['player_id'] != event['player_id']:
                issues.append('Unresolved supersession: ' + old_id)
            elif (timestamp(event['published_at']) > timestamp(old['published_at']) and
                  quality[event['quality']] >= quality[old['quality']]):
                inactive.add(old_id)
            else:
                issues.append('Insufficient evidence to supersede: ' + old_id)
    active, seen = [], set()
    for event in by_id.values():
        fingerprint = (event['player_id'], event.get('original_event_id') or
                       (event['original_source'], event['type'], event['event_at']))
        if event['event_id'] not in inactive and fingerprint not in seen:
            active.append(event)
            seen.add(fingerprint)
    return {'active': active, 'scheduled': scheduled, 'inactive_ids': sorted(inactive), 'warnings': issues}


def apply_adjustments(points, adjustments, records):
    applied, seen = [], set()
    included = {event for record in records for event in record.get('incorporated_events', [])}
    for adj in adjustments:
        if not all(adj.get(k) for k in ('adjustment_id', 'event_id', 'assumption', 'reason')):
            raise ValueError('Adjustment requires identity, event, changed assumption and reason')
        if adj['event_id'] in seen or adj['event_id'] in included:
            raise ValueError('News adjustment would double count event: ' + adj['event_id'])
        if adj.get('base_includes_event') is not False:
            raise ValueError('Adjustment must explicitly establish base_includes_event=false')
        import math
        delta = float(adj['points_delta'])
        if not math.isfinite(delta):
            raise ValueError('Adjustment delta must be finite')
        points += delta
        seen.add(adj['event_id'])
        applied.append(adj)
    return points, applied
