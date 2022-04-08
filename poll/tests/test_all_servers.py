"""Test all_servers()."""

import http.client
import json

import pytest
from all_servers import DEFAULT_MASTER_SERVERS_ADDRESS, add_master_servers, all_servers
from gql import Client, gql
from gql.transport.aiohttp import AIOHTTPTransport


@pytest.fixture(name="client")
def fixture_client():
    """Create a Client with an empty database and the production schema."""
    with open("config/schema.graphql", "r") as file:
        schema = file.read()

    address = "graphql:8080"
    connection = http.client.HTTPConnection(address)

    connection.request("POST", "/alter", '{"drop_all": true}')
    response = connection.getresponse()
    assert response.status == 200 and "errors" not in json.loads(response.read())

    connection.request("POST", "/admin/schema", schema)
    response = connection.getresponse()
    assert response.status == 200 and "errors" not in json.loads(response.read())

    return Client(transport=AIOHTTPTransport(url=f"http://{address}/graphql"))


def add_game_servers(client, addresses):
    """Add game servers."""
    client.execute(
        gql(
            """
            mutation($game_servers: [AddGameServerInput!]!) {
                addGameServer(input: $game_servers) {
                    numUids
                }
            }
            """
        ),
        {"game_servers": [{"address": address} for address in addresses]},
    )


def test_all_servers_no_servers(client):
    """Test all_server() when there is no servers already stored."""
    master_servers_address, game_servers_address = all_servers(client)
    assert game_servers_address == []
    assert set(master_servers_address) == DEFAULT_MASTER_SERVERS_ADDRESS


def test_all_servers_some_master_servers(client):
    """Test all_server() when there is some master servers already stored."""
    addresses = {
        "master-server-test1:8080",
        "master-server-test2:8080",
    }

    add_master_servers(client, list(addresses))

    master_servers_address, game_servers_address = all_servers(client)
    assert game_servers_address == []
    assert set(master_servers_address) == DEFAULT_MASTER_SERVERS_ADDRESS | addresses


def test_all_servers_some_default_master_servers(client):
    """Test all_server() when there is some default master servers already stored."""
    add_master_servers(client, list(DEFAULT_MASTER_SERVERS_ADDRESS))

    master_servers_address, game_servers_address = all_servers(client)
    assert game_servers_address == []
    assert set(master_servers_address) == DEFAULT_MASTER_SERVERS_ADDRESS


def test_all_servers_some_game_servers(client):
    """Test all_server() when there is some game servers already stored."""
    addresses = {
        "game-server-test1:8080",
        "game-server-test2:8080",
    }

    add_game_servers(client, list(addresses))

    master_servers_address, game_servers_address = all_servers(client)
    assert set(game_servers_address) == addresses
    assert set(master_servers_address) == DEFAULT_MASTER_SERVERS_ADDRESS
