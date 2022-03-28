"""
Common fixtures for tests.
"""

import pytest

import frontend.app
import shared.database.graphql
import backend.database.gametype
import backend.database.map


shared.database.graphql.init('dgraph-alpha', '8080', True)


@pytest.fixture(autouse=True)
def fixture_reset_databases():
    """
    Empty databases before each test.
    """

    shared.database.graphql.drop_all_data()


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
