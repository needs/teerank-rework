"""
Test playtime feature.
"""

from backend.playtime import update
from backend.database.player_info import get as player_info_get
from backend.database.gametype import id_none as gametype_id_none
from backend.database.map import get as map_get

def playtime(map_id: str, client: dict) -> int:
    """
    Return client playtime on the map.
    """

    return player_info_get(map_id, client['player']['name'])['playtime']


def test_playtime_no_client(game_server):
    """
    Test playtime when server has no clients.
    """

    update(10, game_server)


def test_playtime_gametype_map(map_, game_server, client1, client2):
    """
    Test playtime on (gametype, map).
    """

    update(10, game_server)

    map_id = map_['id']

    assert playtime(map_id, client1) == 10
    assert playtime(map_id, client2) == 10


def test_playtime_gametype_all(map_, game_server, client1, client2):
    """
    Test playtime on (gametype, all).
    """

    update(10, game_server)

    map_id = map_get(map_['gameType']['id'], None, 'id')['id']

    assert playtime(map_id, client1) == 10
    assert playtime(map_id, client2) == 10


def test_playtime_all_map(map_, game_server, client1, client2):
    """
    Test playtime on (all, map).
    """

    update(10, game_server)

    map_id = map_get(gametype_id_none(), map_['name'], 'id')['id']

    assert playtime(map_id, client1) == 10
    assert playtime(map_id, client2) == 10


def test_playtime_all_all(game_server, client1, client2):
    """
    Test playtime on (all, all).
    """

    update(10, game_server)

    map_id = map_get(gametype_id_none(), None, 'id')['id']

    assert playtime(map_id, client1) == 10
    assert playtime(map_id, client2) == 10
