"""
Playtime management.
"""

from backend.database.map import get as map_get, query as map_query
from backend.database.gametype import id_none as gametype_id_none
import backend.database.player_info

def update(elapsed: int, state: dict) -> None:
    """
    Update all necessary playtimes given the server state and elapsed time.
    """

    if len(state['clients']) == 0:
        return

    names = [client['player']['name'] for client in state['clients']]
    map_ = map_query(state['map']['id'], "name, gameType { id }")

    map_ids = [
        state['map']['id'],
        map_get(map_['gameType']['id'], None, 'id')['id'],
        map_get(gametype_id_none(), map_['name'], 'id')['id'],
        map_get(gametype_id_none(), None, 'id')['id']
    ]

    players_info = backend.database.player_info.get_many(map_ids, names)

    for player_info in players_info:
        player_info['playtime'] += elapsed

    backend.database.player_info.set_many(players_info)
