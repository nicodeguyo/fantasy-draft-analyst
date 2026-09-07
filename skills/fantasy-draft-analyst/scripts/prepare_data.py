#!/usr/bin/env python3
"""Build an auditable league-scored pool from schema-v1 evidence.

  prepare_data.py --league league.json --snapshot evidence.json --out players.csv
  prepare_data.py --league league.json --season 2026 --fetch-espn --out players.csv
  prepare_data.py --league league.json --snapshot evidence.json --projection-import fp-import.json --out players.csv

Projection-import manifests name a CSV, source, independence_group, URL, fetched_at,
updated_at, season and period. Optional column_map explicitly maps canonical stat
names to unique provider headers; assumed_zeros documents unsupported categories.
FantasyPros exports can use this path without requiring a paid API. Never import
FPTS as stat projections or positional ranks as ADP. Output sidecar contains all
inputs, failures and quarantined records. Legacy scoring.py is not this strict path.
"""
import argparse
import csv
import hashlib
import json
from pathlib import Path
import sys
from fantasy_core.evidence import prepare_snapshot
from fantasy_core.providers import fetch_espn, import_projection_csv, fetch_projection_tables
from scoring import load_league

FIELDS = ['name','pos','team','adp','adp_sd','proj','bye','note','player_id','projection_sd','source_count','independent_sources','evidence_mode','expected_games','projection_convention','performance_sd']


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--league', required=True)
    ap.add_argument('--snapshot')
    ap.add_argument('--season', type=int)
    ap.add_argument('--fetch-espn', action='store_true')
    ap.add_argument('--fetch-fantasypros', action='store_true')
    ap.add_argument('--fetch-cbs', action='store_true')
    ap.add_argument('--projection-import', action='append', default=[])
    ap.add_argument('--out', required=True)
    ap.add_argument('--as-of', help='Explicit ISO timestamp for reproducible offline analysis')
    ap.add_argument('--max-age-days', type=float, default=3)
    args = ap.parse_args()
    try:
        league = load_league(args.league)
        if not args.snapshot and not args.season:
            ap.error('--snapshot or --season is required')
        snapshot = json.loads(Path(args.snapshot).read_text()) if args.snapshot else {
            'schema_version': 1, 'season': args.season, 'period': 'season', 'players': []}
        if args.season and snapshot['season'] != args.season:
            raise ValueError('--season differs from snapshot')
        imports, failures = [], []
        if args.fetch_espn:
            try:
                fresh = fetch_espn(snapshot['season'])
                # Explicit IDs preserve canonical identities and other providers.
                existing = {str(p.get('provider_ids', {}).get('espn')):p for p in snapshot['players'] if p.get('provider_ids', {}).get('espn') is not None}
                for player in fresh:
                    old = existing.get(player['provider_ids']['espn'])
                    if old:
                        old['projections'] = [r for r in old.get('projections', []) if r.get('source') != 'espn'] + player['projections']
                        old['adp'] = player['adp']
                        old['team'] = player['team']
                    else:
                        snapshot['players'].append(player)
            except Exception as exc:
                failures.append({'source':'espn','error':str(exc)})
        for source, enabled in [('fantasypros',args.fetch_fantasypros),('cbs',args.fetch_cbs)]:
            if enabled:
                additions,audits,source_failures=fetch_projection_tables(source,snapshot['season'],snapshot['players'])
                imports.extend(audits);failures.extend(source_failures)
                for player in snapshot['players']:
                    if player['player_id'] in additions:
                        player['projections']=[r for r in player.get('projections',[]) if r.get('source')!=source]+[additions[player['player_id']]]
        for manifest_path in args.projection_import:
            manifest = json.loads(Path(manifest_path).read_text())
            try:
                csv_path = Path(manifest.pop('csv'))
                if not csv_path.is_absolute():
                    csv_path = Path(manifest_path).parent / csv_path
                additions, audit = import_projection_csv(csv_path.read_text(encoding='utf-8-sig'), registry=snapshot['players'], **manifest)
                for player in snapshot['players']:
                    if player['player_id'] in additions:
                        source = additions[player['player_id']]['source']
                        player['projections'] = [r for r in player.get('projections', []) if r.get('source') != source] + [additions[player['player_id']]]
                imports.append(audit)
            except (ValueError, TypeError, KeyError, OSError) as exc:
                failures.append({'manifest':manifest_path,'error':str(exc)})
        rows, report = prepare_snapshot(snapshot, league, now=args.as_of, max_age_days=args.max_age_days)
        report.update(imports=imports, source_failures=failures)
        if failures and report['mode'] == 'full':
            report['mode'] = 'limited'
        revision_input = {'snapshot':snapshot,'league':league,'as_of':report['as_of'],'max_age_days':args.max_age_days}
        report['data_revision'] = hashlib.sha256(json.dumps(revision_input,sort_keys=True,allow_nan=False).encode()).hexdigest()
        output = Path(args.out)
        output.parent.mkdir(parents=True,exist_ok=True)
        # Weekly/rest-of-season data may be inspected, but cannot masquerade as a season pool.
        with output.open('w',newline='') as stream:
            writer = csv.DictWriter(stream,fieldnames=FIELDS)
            writer.writeheader()
            if report['engine_eligible']:
                writer.writerows(rows)
        sidecar = output.with_suffix('.evidence.json')
        sidecar.write_text(json.dumps(report,indent=2,allow_nan=False)+'\n')
        print(json.dumps({'mode':report['mode'],'engine_eligible':report['engine_eligible'],
                          'players':len(rows),'report':str(sidecar),'source_failures':len(failures)}))
        return 0
    except (ValueError, KeyError, OSError) as exc:
        print('Evidence preparation failed: '+str(exc),file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
