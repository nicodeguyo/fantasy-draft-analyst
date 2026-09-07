"""Public/authorized provider adapters; imports never distribute vendor datasets.

ESPN stat IDs are checked against the requested season/split. FantasyPros adapter
accepts a user-exported raw stat CSV, NOT vendor fantasy-point columns. Provider
access is fallible; callers retain failures in the evidence report.
"""
import csv
import io
import json
import urllib.request
from datetime import datetime, timezone
from .identity import IdentityIndex

ESPN_STATS = {'pass_yd': '3', 'pass_td': '4', 'int': '20', 'rush_yd': '24',
              'rush_td': '25', 'rec': '53', 'rec_yd': '42', 'rec_td': '43', 'fum': '72', 'fg': '83', 'fg_miss': '85', 'xp': '86',
              'sacks': '99', 'def_int': '95', 'fum_rec': '96', 'def_td': '105',
              'safety': '98', 'pts_allowed': '120'}
POSITIONS = {1: 'QB', 2: 'RB', 3: 'WR', 4: 'TE', 5: 'K', 16: 'DEF'}
TEAMS = {1:'ATL',2:'BUF',3:'CHI',4:'CIN',5:'CLE',6:'DAL',7:'DEN',8:'DET',9:'GB',10:'TEN',11:'IND',12:'KC',13:'LV',14:'LAR',15:'MIA',16:'MIN',17:'NE',18:'NO',19:'NYG',20:'NYJ',21:'PHI',22:'ARI',23:'PIT',24:'LAC',25:'SF',26:'SEA',27:'TB',28:'WAS',29:'CAR',30:'JAX',33:'BAL',34:'HOU'}


def espn_url(season):
    return f'https://lm-api-reads.fantasy.espn.com/apis/v3/games/ffl/seasons/{int(season)}/segments/0/leaguedefaults/3?view=kona_player_info'


def fetch_espn(season, timeout=20):
    filters = {'players': {'limit': 1000, 'sortDraftRanks': {'sortPriority': 100, 'sortAsc': True, 'value': 'PPR'}}}
    request = urllib.request.Request(espn_url(season), headers={
        'User-Agent': 'fantasy-draft-analyst (public projection research)',
        'X-Fantasy-Filter': json.dumps(filters)})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        data = json.load(response)
    return espn_players(data, season, datetime.now(timezone.utc).isoformat())


def espn_players(data, season, fetched_at):
    result = []
    if not isinstance(data.get('players'), list):
        raise ValueError('ESPN payload lacks players list')
    for item in data['players']:
        player = item.get('player', item)
        pid = player.get('id')
        if pid is None:
            raise ValueError('ESPN player lacks stable ID')
        pos = POSITIONS.get(player.get('defaultPositionId'), 'UNKNOWN')
        records = []
        for split in player.get('stats', []):
            if split.get('seasonId') != season or split.get('statSourceId') != 1 or split.get('statSplitTypeId') != 0:
                continue
            raw = split.get('stats', {})
            stats = {name: raw[stat] for name, stat in ESPN_STATS.items() if stat in raw}
            assumptions = {'two_pt': 'ESPN adapter does not currently map two-point projections'} if pos in ('QB','RB','WR','TE') else {}
            if pos == 'QB':
                for key in ('rec', 'rec_yd', 'rec_td'):
                    if key not in stats:
                        assumptions[key] = 'ESPN QB receiving absent; explicit zero approximation'
            if pos == 'TE':
                for key in ('rush_yd', 'rush_td'):
                    if key not in stats:
                        assumptions[key] = 'ESPN TE rushing absent; explicit zero approximation'
            records.append({'source': 'espn', 'independence_group': 'espn', 'independence_verified': True, 'season': season,
                            'period': 'season', 'fetched_at': fetched_at, 'updated_at': None,
                            'url': espn_url(season), 'stats': stats,
                            'assumed_zeros': assumptions,
                            'raw_stats': raw, 'expected_games': raw.get('210'),
                            'stat_definition_reference': 'https://github.com/cwendt94/espn-api/blob/master/espn_api/football/constant.py',
                            'incorporated_events': []})
        adp = (player.get('ownership') or {}).get('averageDraftPosition')
        result.append({'player_id': 'espn:' + str(pid), 'name': player.get('fullName', ''), 'pos': pos,
                       'team': TEAMS.get(player.get('proTeamId'), ''), 'provider_ids': {'espn': str(pid)},
                       'projections': records,
                       'adp': {'value': adp, 'source': 'espn', 'season': season, 'format': 'managed-1qb',
                               'updated_at': fetched_at, 'timestamp_basis': 'observation, provider update unavailable'}})
    if not result:
        raise ValueError('ESPN returned an empty player pool')
    return result


def import_projection_csv(text, *, source, independence_group, season, period, fetched_at,
                          updated_at, url, registry, column_map=None, week=None,
                          assumed_zeros=None, constituents=None, independence_verified=False):
    """Explicit semantic map prevents duplicate YDS / rank / FPTS confusion.

    column_map maps canonical names (name, rec_yd, etc.) to exact CSV headers.
    Canonical headers work without a map. Unresolved rows remain quarantined.
    Returns additions keyed by canonical ID and a human-readable import audit.
    """
    index = IdentityIndex(registry)
    reader = csv.DictReader(io.StringIO(text))
    headers = reader.fieldnames or []
    if not headers or len(headers) != len(set(headers)):
        raise ValueError('CSV headers missing or duplicated; use unique stat-group headers')
    mapping = column_map or {h: h for h in headers}
    if 'name' not in mapping and 'player_id' not in mapping and 'provider_id' not in mapping:
        raise ValueError('Explicit name or ID column required')
    for canonical, header in mapping.items():
        if header not in headers:
            raise ValueError('Mapped column absent: ' + header)
    additions, unresolved = {}, []
    stats_keys = {'pass_yd','pass_td','int','rush_yd','rush_td','rec','rec_yd','rec_td','fum','two_pt','fg','fg_miss','xp','sacks','def_int','fum_rec','def_td','safety','pts_allowed'}
    for rownum, row in enumerate(reader, 2):
        mapped = {canonical: row[header] for canonical, header in mapping.items()}
        player, status = index.resolve(player_id=mapped.get('player_id') or None, name=mapped.get('name'),
                                       source=source, provider_id=mapped.get('provider_id') or None)
        if not player:
            unresolved.append({'row': rownum, 'status': status, 'raw': row})
            continue
        record = {'source': source, 'independence_group': independence_group, 'season': season, 'period': period,
                  'fetched_at': fetched_at, 'updated_at': updated_at, 'url': url,
                  'stats': {k: mapped[k] for k in stats_keys if k in mapped},
                  'assumed_zeros': assumed_zeros or {}, 'transformation': {'column_map': mapping, 'row': rownum},
                  'constituents': constituents, 'independence_verified': independence_verified}
        if week is not None:
            record['week'] = week
        if player['player_id'] in additions:
            unresolved.append({'row': rownum, 'status': 'duplicate matched player', 'raw': row})
            # Do not silently choose either duplicate projection.
            additions[player['player_id']] = None
        else:
            additions[player['player_id']] = record
    return {k:v for k,v in additions.items() if v is not None}, {'source':source,'column_map':mapping,'quarantine':unresolved}

# Public tables have grouped repeated YDS/TD headers. Read their documented
# position-specific layout; fail closed on drift rather than offsetting columns.
from html.parser import HTMLParser
import re


class ProjectionTables(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tables=[]; self.table=None; self.row=None; self.cell=None; self.link=None

    def handle_starttag(self, tag, attrs):
        attrs=dict(attrs)
        if tag=='table': self.table=[]
        elif tag=='tr' and self.table is not None: self.row=[]
        elif tag in ('td','th') and self.row is not None: self.cell={'text':'','links':[]}
        elif tag=='a' and self.cell is not None: self.link={'href':attrs.get('href',''),'text':'','name':attrs.get('fp-player-name')}

    def handle_data(self,data):
        if self.cell is not None:self.cell['text']+=data
        if self.link is not None:self.link['text']+=data

    def handle_endtag(self,tag):
        if tag=='a' and self.link is not None and self.cell is not None:
            self.cell['links'].append(self.link);self.link=None
        elif tag in ('td','th') and self.cell is not None:
            self.cell['text']=' '.join(self.cell['text'].split());self.row.append(self.cell);self.cell=None
        elif tag=='tr' and self.row is not None and self.table is not None:
            self.table.append(self.row);self.row=None
        elif tag=='table' and self.table is not None:
            self.tables.append(self.table);self.table=None


FP_HEADERS={
 'QB':['Player','ATT','CMP','YDS','TDS','INTS','ATT','YDS','TDS','FL','FPTS'],
 'RB':['Player','ATT','YDS','TDS','REC','YDS','TDS','FL','FPTS'],
 'WR':['Player','REC','YDS','TDS','ATT','YDS','TDS','FL','FPTS'],
 'TE':['Player','REC','YDS','TDS','FL','FPTS']}
FP_COLUMNS={
 'QB':{3:'pass_yd',4:'pass_td',5:'int',7:'rush_yd',8:'rush_td',9:'fum'},
 'RB':{2:'rush_yd',3:'rush_td',4:'rec',5:'rec_yd',6:'rec_td',7:'fum'},
 'WR':{1:'rec',2:'rec_yd',3:'rec_td',5:'rush_yd',6:'rush_td',7:'fum'},
 'TE':{1:'rec',2:'rec_yd',3:'rec_td',4:'fum'}}
CBS_COLUMNS={'Passing Yards':'pass_yd','Passing Touchdowns':'pass_td','Touchdowns Passes':'pass_td','Interceptions':'int','Interceptions Thrown':'int',
 'Rushing Yards':'rush_yd','Rushing Touchdowns':'rush_td','Receptions':'rec',
 'Receiving Yards':'rec_yd','Receiving Touchdowns':'rec_td','Fumbles Lost':'fum'}


def projection_url(source,pos,season):
    if source=='fantasypros':
        return f'https://www.fantasypros.com/nfl/projections/{pos.lower()}.php?week=draft&scoring=HALF&year={int(season)}'
    if source=='cbs':
        return f'https://www.cbssports.com/fantasy/football/stats/{pos}/{int(season)}/season/projections/nonppr/'
    raise ValueError('Unsupported public projection source')


def parse_projection_html(html, *, source, pos, season, fetched_at, registry):
    if pos not in FP_HEADERS:
        raise ValueError('Public table adapter currently supports QB/RB/WR/TE only')
    title=re.search(r'<h1[^>]*>(.*?)</h1>',html,re.S|re.I)
    heading=re.sub('<[^>]+>','',title.group(1)) if title else ''
    if str(season) not in heading or 'Projection' not in heading or re.search(r'Week\s+\d',heading,re.I):
        raise ValueError('Provider page does not confirm requested full-season projections')
    parser=ProjectionTables();parser.feed(html)
    selected=None;columns={};games_column=None
    for table in parser.tables:
        for i,row in enumerate(table):
            texts=[cell['text'] for cell in row]
            if source=='fantasypros' and texts==FP_HEADERS[pos]:
                selected=table[i+1:];columns=FP_COLUMNS[pos];break
            if source=='cbs' and texts and texts[0]=='Player':
                for j,text in enumerate(texts):
                    for description,canonical in CBS_COLUMNS.items():
                        if text.endswith(description):columns[j]=canonical
                    if text.endswith('Games Played'):games_column=j
                if columns:selected=table[i+1:];break
        if selected is not None:break
    if selected is None:
        raise ValueError('Projection table headers changed or table unavailable')
    index=IdentityIndex(registry);additions={};quarantine=[]
    update=re.search(r'<time[^>]*datetime=[\"\']([^\"\']+)',html,re.I)
    for rownum,row in enumerate(selected,1):
        if not row or not row[0]['links']:continue
        links=[link for link in row[0]['links'] if '/nfl/' in link['href']]
        if not links:continue
        link=links[-1]  # CBS's final link is full name, first is abbreviated.
        name=link['name'] or link['text'].strip()
        player,status=index.resolve(name=name)
        if not player:
            quarantine.append({'name':name,'status':status,'row':rownum});continue
        if player['pos']!=pos:
            quarantine.append({'name':name,'status':'position mismatch','row':rownum});continue
        if max(columns)>=len(row):
            raise ValueError('Projection row width differs from headers')
        stats={canonical:row[i]['text'] for i,canonical in columns.items()}
        assumptions={'two_pt':'Source table does not publish two-point projections; explicit zero approximation'}
        # No rushing/receiving omission is hidden as a structural zero.
        if pos=='QB':
            for k in ('rec','rec_yd','rec_td'):
                if k not in stats:assumptions[k]='QB receiving not supplied by this table; explicit zero approximation'
        if pos=='TE':
            for k in ('rush_yd','rush_td'):
                if k not in stats:assumptions[k]='TE rushing not supplied by this table; explicit zero approximation'
        record={'source':source,'independence_group':source,'season':season,'period':'season',
                'url':projection_url(source,pos,season),'fetched_at':fetched_at,'updated_at':None,
                'provider_updated_text':update.group(1) if update else None,
                'update_time_note':'Provider timestamp timezone is unknown; not promoted to a verified UTC update',
                'stats':stats,'assumed_zeros':assumptions,'independence_verified':source=='cbs',
                'constituents':None if source=='fantasypros' else ['cbs'],
                'transformation':{'position':pos,'column_indices':columns,'vendor_FPTS_ignored':True}}
        if games_column is not None:
            record['expected_games']=row[games_column]['text']
        pid=player['player_id']
        if pid in additions:
            quarantine.append({'name':name,'status':'duplicate matched player','row':rownum})
            additions[pid]=None
        else:additions[pid]=record
    return {k:v for k,v in additions.items() if v is not None}, {'source':source,'pos':pos,'url':projection_url(source,pos,season),
        'matched':sum(v is not None for v in additions.values()),'quarantine':quarantine,
        'coverage_note':'Only rows returned by public page are included; absent players remain uncovered'}


def fetch_projection_tables(source,season,registry,timeout=20):
    additions={};audits=[];failures=[]
    for pos in FP_HEADERS:
        try:
            req=urllib.request.Request(projection_url(source,pos,season),headers={'User-Agent':'Mozilla/5.0 (fantasy-draft-analyst)'})
            with urllib.request.urlopen(req,timeout=timeout) as response:
                html=response.read().decode('utf-8')
            parsed,audit=parse_projection_html(html,source=source,pos=pos,season=season,
                    fetched_at=datetime.now(timezone.utc).isoformat(),registry=registry)
            additions.update(parsed);audits.append(audit)
        except (ValueError,OSError) as exc:
            failures.append({'source':source,'pos':pos,'error':str(exc)})
    return additions,audits,failures
