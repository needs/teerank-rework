"""
Common fixtures for tests.
"""

import pytest

import frontend.app
import shared.database.graphql
import backend.database.gametype
import backend.database.map
from backend.game_server import GameServerType


shared.database.graphql.init('dgraph-alpha', '8080', True)


@pytest.fixture(autouse=True)
def fixture_reset_databases():
    """
    Empty databases before each test.
    """

    shared.database.graphql.drop_all_data()


@pytest.fixture(autouse=True)
def fixture_clear_cache():
    """
    Clear caches so that cached value during previous tests don't interfer with
    the current test.
    """

    backend.database.map.get.id_none = None
    backend.database.gametype.get.id_none = None


@pytest.fixture(name='app', scope='session')
def fixture_app():
    """
    Flask fixture for our application.

    Since tests will use the test client rather than this fixture directly,
    bounding it to the session scope works and will improve performances.
    """

    app = frontend.app.create_app()
    app.testing = True

    return app


@pytest.fixture(name='client')
def fixture_client(app):
    """
    Create a test client for our application.
    """

    return app.test_client()


@pytest.fixture(name='gametype')
def fixture_gametype():
    """
    Create a new gametype and return it.
    """

    return backend.database.gametype.get('CTF')


@pytest.fixture(name='map_')
def fixture_map(gametype):
    """
    Create a new map and return it.
    """

    return backend.database.map.get(gametype['id'], 'ctf1')


@pytest.fixture(name='game_server')
def fixture_game_server(map_):
    """
    Create a game server and return it.
    """

    return {
        'type': GameServerType.VANILLA,
        'address': '0.0.0.0:8300',
        'version': '0.0.1',
        'name': 'test-gameserver',
        'map': backend.database.map.ref(map_['id']),
        'numPlayers': 0,
        'maxPlayers': 16,
        'numClients': 0,
        'maxClients': 16,

        'clients': []
    }


def _game_server_add_client(game_server, name, score, ingame=True):
    """
    Adds a client to the given game server.
    """

    client = {
        'player': backend.database.player.ref(name),
        'clan': backend.database.clan.ref(None),
        'country': 0,
        'score': score,
        'ingame': ingame,
        'gameServer': backend.database.game_server.ref(game_server['address'])
    }

    game_server['clients'].append(client)

    game_server['numClients'] += 1
    if ingame:
        game_server['numPlayers'] += 1

    return client


@pytest.fixture(name='client1')
def fixture_client1(game_server):
    """
    Add a client to the existing game server.
    """

    return _game_server_add_client(game_server, 'test-client1', 0)


@pytest.fixture(name='client2')
def fixture_client2(game_server):
    """
    Add a client to the existing game server.
    """

    return _game_server_add_client(game_server, 'test-client2', 0)
