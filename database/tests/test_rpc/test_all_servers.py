"""Test all_servers()."""

import rpc.all_servers
from rpc.all_servers import DEFAULT_MASTER_SERVERS_ADDRESS, add_master_servers


def add_game_servers(dgraph, addresses):
    """Add game servers."""
    dgraph.execute(
        """
        mutation($game_servers: [AddGameServerInput!]!) {
            addGameServer(input: $game_servers) {
                numUids
            }
        }
        """,
        {"game_servers": [{"address": address} for address in addresses]},
    )


def test_all_servers_no_servers(dgraph):
    """Test all_server() when there is no servers already stored."""
    response = rpc.all_servers.run(dgraph)
    assert response.game_servers_address == []
    assert set(response.master_servers_address) == DEFAULT_MASTER_SERVERS_ADDRESS


def test_all_servers_some_master_servers(dgraph):
    """Test all_server() when there is some master servers already stored."""
    master_servers_address = {
        "master-server-test1:8080",
        "master-server-test2:8080",
    }

    add_master_servers(dgraph, list(master_servers_address))

    response = rpc.all_servers.run(dgraph)
    assert response.game_servers_address == []
    assert (
        set(response.master_servers_address)
        == DEFAULT_MASTER_SERVERS_ADDRESS | master_servers_address
    )


def test_all_servers_some_default_master_servers(dgraph):
    """Test all_server() when there is some default master servers already stored."""
    add_master_servers(dgraph, list(DEFAULT_MASTER_SERVERS_ADDRESS))

    response = rpc.all_servers.run(dgraph)
    assert response.game_servers_address == []
    assert set(response.master_servers_address) == DEFAULT_MASTER_SERVERS_ADDRESS


def test_all_servers_some_game_servers(dgraph):
    """Test all_server() when there is some game servers already stored."""
    game_servers_address = {
        "game-server-test1:8080",
        "game-server-test2:8080",
    }

    add_game_servers(dgraph, list(game_servers_address))

    response = rpc.all_servers.run(dgraph)
    assert set(response.game_servers_address) == game_servers_address
    assert set(response.master_servers_address) == DEFAULT_MASTER_SERVERS_ADDRESS
