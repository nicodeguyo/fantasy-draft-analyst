"""Conservative identity resolution: no team/last-name guesses or fuzzy auto-merges."""
import re
import unicodedata


def key(name):
    name = unicodedata.normalize('NFKD', str(name)).encode('ascii', 'ignore').decode().lower()
    return re.sub(r'[^a-z0-9]', '', name)


class IdentityIndex:
    def __init__(self, players):
        self.ids, self.names, self.provider_ids = {}, {}, {}
        for player in players:
            pid = player.get('player_id')
            if not pid or pid in self.ids:
                raise ValueError('Missing or duplicate player_id: %r' % pid)
            self.ids[pid] = player
            for name in [player.get('name', ''), *player.get('aliases', [])]:
                if key(name):
                    self.names.setdefault(key(name), set()).add(pid)
            for source, value in player.get('provider_ids', {}).items():
                self.provider_ids.setdefault((source, str(value)), set()).add(pid)

    def resolve(self, *, player_id=None, name=None, source=None, provider_id=None):
        if player_id is not None:
            return self.ids.get(player_id), 'matched' if player_id in self.ids else 'unknown'
        matches = self.provider_ids.get((source, str(provider_id)), set()) if provider_id is not None else self.names.get(key(name or ''), set())
        if len(matches) == 1:
            return self.ids[next(iter(matches))], 'matched'
        return None, 'ambiguous' if matches else 'unknown'
