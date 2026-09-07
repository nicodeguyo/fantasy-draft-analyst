"""Versioned, replayable local snake-draft sessions. No provider calls on pick path."""
from __future__ import annotations
import copy
from contextlib import contextmanager
import hashlib
import json
import os
import tempfile
import uuid
from datetime import datetime, timezone
from pathlib import Path

SCHEMA_VERSION = 1

def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, allow_nan=False).encode()).hexdigest()

def now():
    return datetime.now(timezone.utc).isoformat()

def normalize_players(players):
    out, ids, names = [], set(), set()
    for raw in players:
        p = dict(raw)
        name = str(p.get("name", "")).strip()
        pid = str(p.get("player_id") or p.get("id") or "name:" + name.casefold())
        if not name or pid in ids:
            raise ValueError("Players require unique IDs and nonempty names")
        p.update(player_id=pid, name=name)
        ids.add(pid); names.add(name.casefold()); out.append(p)
    if not out:
        raise ValueError("Player pool is empty")
    return out

def owner_at(league, pick):
    c = league["league"]
    n = int(c["teams"])
    r, offset = divmod(pick - 1, n)
    return n - offset if c.get("draft_type", "snake") == "snake" and r % 2 else offset + 1

def create(league, players, evidence=None):
    c = league["league"]
    if c.get("draft_type", "snake") not in ("snake", "linear"):
        raise ValueError("Live sessions support snake and linear drafts only")
    if int(c["teams"]) < 2 or not 1 <= int(c["draft_slot"]) <= int(c["teams"]) or int(c["rounds"]) < 1:
        raise ValueError("Invalid league teams, slot or rounds")
    players = normalize_players(players)
    s = dict(schema_version=1, session_id=str(uuid.uuid4()), league=copy.deepcopy(league), players=players,
             evidence=evidence or {"mode":"limited", "warnings":["Legacy pool: source provenance unverified"]},
             data_revision=digest([players,evidence]), revision=0, events=[], receipts=[], snapshots={}, created_at=now())
    s["snapshots"][s["data_revision"]] = {"players":copy.deepcopy(players),"evidence":copy.deepcopy(s["evidence"])}
    keepers = league.get("keepers", {})
    if int(keepers.get("count", 0)) > 1:
        raise ValueError("Only one keeper per team is supported")
    for k in keepers.get("league_keeper_list", []):
        if k.get("round") is None or k.get("draft_slot") is None:
            raise ValueError("Confirmed keepers require an explicit round and draft_slot")
        slot, rnd, n = int(k["draft_slot"]), int(k["round"]), int(c["teams"])
        pick = (rnd-1)*n + (n-slot+1 if c.get("draft_type","snake") == "snake" and rnd%2 == 0 else slot)
        record_pick(s, k.get("player_id") or k.get("player"), pick=pick, owner=slot, keeper=True,
                    event_id="keeper:"+str(slot))
    return s

def replay(s):
    if s.get("schema_version") != SCHEMA_VERSION:
        raise ValueError("Unsupported session schema; explicit migration required")
    undone = {e["target"] for e in s["events"] if e["type"] == "undo"}
    picks = [copy.deepcopy(e["payload"]) for e in s["events"] if e["type"] == "pick" and e["id"] not in undone]
    corrections={e["pick"]:e["player"] for e in s["events"] if e["type"]=="resolve" and e["target"] not in undone}
    for p in picks:
        if p["unknown"] and p["pick"] in corrections:
            p.update(corrections[p["pick"]],unknown=False)
    picks.sort(key=lambda x:x["pick"])
    used = {p["pick"] for p in picks}
    current = 1
    while current in used: current += 1
    return {"picks":picks, "current_pick":current, "complete":current > int(s["league"]["league"]["teams"])*int(s["league"]["league"]["rounds"])}

def token(s):
    return digest({"revision":s["revision"], "data":s["data_revision"], "league":s["league"], "picks":replay(s)["picks"]})

def resolve(s, value):
    match = [p for p in s["players"] if value == p["player_id"] or str(value).casefold() == p["name"].casefold()]
    return match[0] if len(match)==1 else None

def append(s, event):
    s["events"].append(event)
    s["revision"] += 1

def record_pick(s, value, pick=None, owner=None, keeper=False, event_id=None, recommendation=None):
    event_id = event_id or str(uuid.uuid4())
    existing = next((e for e in s["events"] if e["id"] == event_id),None)
    if existing:
        if existing["type"] != "pick": raise ValueError("Event ID already belongs to another operation")
        old = existing["payload"]
        p = resolve(s,value)
        if (p["player_id"] if p else None) != old["player_id"] or str(value) not in (old["name"], old["player_id"]) or (pick is not None and int(pick)!=old["pick"]):
            raise ValueError("Event ID reused with conflicting pick")
        return existing
    state = replay(s)
    pick = state["current_pick"] if pick is None else int(pick)
    total = int(s["league"]["league"]["teams"])*int(s["league"]["league"]["rounds"])
    if not 1<=pick<=total or any(p["pick"] == pick for p in state["picks"]):
        raise ValueError("Pick is outside draft or already occupied")
    expected = owner_at(s["league"],pick)
    owner = expected if owner is None else int(owner)
    if owner != expected: raise ValueError("Owner does not match snake/linear pick; traded picks unsupported")
    p = resolve(s,value)
    if keeper and p is None: raise ValueError("Keeper must resolve to a known player")
    if not str(value or "").strip(): raise ValueError("Unknown selection requires its original name")
    if p and any(x["player_id"] == p["player_id"] for x in state["picks"]):
        raise ValueError("Player is already drafted or kept")
    if keeper and any(x["keeper"] and x["owner"] == owner for x in state["picks"]):
        raise ValueError("Only one keeper per team is supported")
    payload = dict(pick=pick, owner=owner, player_id=p["player_id"] if p else None,
                   name=p["name"] if p else str(value), keeper=keeper, unknown=p is None)
    if recommendation is not None and recommendation.get("state_token") != token(s):
        raise ValueError("Recommendation is stale; refresh before confirming the pick")
    event = dict(id=event_id, type="pick", timestamp=now(), payload=payload)
    if owner == int(s["league"]["league"]["draft_slot"]) and not keeper:
        s["receipts"].append(dict(event_id=event_id, state_token=token(s), data_revision=s["data_revision"],
             pick=pick, roster=[x for x in state["picks"] if x["owner"]==owner],
             available_ids=[x["player_id"] for x in available(s)], evidence=copy.deepcopy(s["evidence"]),
             recommendation=copy.deepcopy(recommendation), choice=payload, timestamp=now()))
    append(s,event)
    return event

def undo(s, event_id=None):
    undone = {e["target"] for e in s["events"] if e["type"] == "undo"}
    target = next((e for e in reversed(s["events"]) if e["type"]=="pick" and e["id"] not in undone and not e["payload"]["keeper"]),None)
    if target is None: raise ValueError("No non-keeper pick to undo")
    event=dict(id=event_id or str(uuid.uuid4()), type="undo", target=target["id"], timestamp=now())
    if any(e["id"]==event["id"] for e in s["events"]): raise ValueError("Duplicate undo event ID")
    append(s,event)
    return event

def resolve_unknown(s,pick,player):
    pick=int(pick)
    old=next((p for p in replay(s)['picks'] if p['pick']==pick and p['unknown']),None)
    p=resolve(s,player)
    if old is None or p is None:raise ValueError('Resolution requires an unmatched pick and a known player')
    if any(x['player_id']==p['player_id'] for x in replay(s)['picks']):raise ValueError('Resolved player is already drafted')
    undone={e['target'] for e in s['events'] if e['type']=='undo'}
    target=next(e['id'] for e in s['events'] if e['type']=='pick' and e['payload']['pick']==pick and e['id'] not in undone)
    append(s,dict(id=str(uuid.uuid4()),type='resolve',target=target,pick=pick,player={'player_id':p['player_id'],'name':p['name']},timestamp=now()))


def available(s):
    taken={p["player_id"] for p in replay(s)["picks"] if p["player_id"]}
    return [p for p in s["players"] if p["player_id"] not in taken]

def refresh(s, players, evidence=None):
    new=normalize_players(players)
    # Retain known drafted identities if a provider temporarily drops a player.
    taken={p["player_id"] for p in replay(s)["picks"] if p["player_id"]}
    ids={p["player_id"] for p in new}
    retained = [dict(p,evidence_mode="retained_stale") for p in s["players"] if p["player_id"] in taken-ids]
    new += retained
    old=s["data_revision"]
    old_names={}
    for p in s["players"]:old_names.setdefault(p["name"].casefold(),set()).add(p["player_id"])
    if any(p["name"].casefold() in old_names and p["player_id"] not in old_names[p["name"].casefold()] for p in new):
        raise ValueError("Refresh changed a known player ID; resolve identity mapping before refresh")
    s.setdefault("snapshots",{})[old]={"players":copy.deepcopy(s["players"]),"evidence":copy.deepcopy(s["evidence"])}
    s["players"]=new
    s["evidence"]=copy.deepcopy(evidence) if evidence is not None else {"mode":"limited","warnings":["Refreshed pool has no matching evidence report; source provenance unverified"]}
    if retained:
        s["evidence"]["mode"]="limited"
        s["evidence"].setdefault("warnings",[]).append("Drafted players absent from refreshed feed retain previous values; treat their estimates as stale: "+", ".join(p["name"] for p in retained))
    s["data_revision"]=digest([new,s["evidence"]])
    s["snapshots"][s["data_revision"]]={"players":copy.deepcopy(new),"evidence":copy.deepcopy(s["evidence"])}
    append(s,dict(id=str(uuid.uuid4()),type="refresh",timestamp=now(),previous_data_revision=old,data_revision=s["data_revision"]))

@contextmanager
def mutation_lock(path):
    """Hold one OS advisory lock across the entire read-modify-atomic-save.

    The persistent lock file is deliberately not removed: unlinking it could let
    another process lock a different inode. OS locks release on process exit.
    """
    lock_path=Path(str(Path(path).resolve())+'.lock')
    lock_path.parent.mkdir(parents=True,exist_ok=True)
    with lock_path.open('a+b') as stream:
        stream.seek(0,os.SEEK_END)
        if stream.tell()==0:
            stream.write(b'0');stream.flush()
        stream.seek(0)
        try:
            if os.name=='nt':
                import msvcrt
                msvcrt.locking(stream.fileno(),msvcrt.LK_NBLCK,1)
            else:
                import fcntl
                fcntl.flock(stream.fileno(),fcntl.LOCK_EX|fcntl.LOCK_NB)
        except OSError as exc:
            raise ValueError('Session is busy in another writer; retry after that action finishes. No changes saved.') from exc
        try:
            yield
        finally:
            stream.seek(0)
            if os.name=='nt':
                msvcrt.locking(stream.fileno(),msvcrt.LK_UNLCK,1)
            else:
                fcntl.flock(stream.fileno(),fcntl.LOCK_UN)


def save(s,path):
    path=Path(path)
    path.parent.mkdir(parents=True,exist_ok=True)
    fd,tmp=tempfile.mkstemp(prefix=path.name+".",suffix=".tmp",dir=path.parent)
    try:
        with os.fdopen(fd,"w",encoding="utf-8") as f:
            json.dump(s,f,indent=2,allow_nan=False); f.flush(); os.fsync(f.fileno())
        os.replace(tmp,path)
    finally:
        if os.path.exists(tmp): os.unlink(tmp)

def load(path):
    s=json.loads(Path(path).read_text(encoding="utf-8"))
    replay(s)
    return s
