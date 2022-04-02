"""Test all_servers()."""

import rpc.all_servers
from rpc.all_servers import DEFAULT_MASTER_SERVERS_ADDRESS, add_master_servers


def test_all_servers_no_servers(dgraph):
    """Test all_server() when there is no servers already stored."""
    response = rpc.all_servers.run(dgraph)
    assert response.game_servers_address == []
    assert set(response.master_servers_address) == DEFAULT_MASTER_SERVERS_ADDRESS


def test_all_servers_some_master_servers(dgraph):
    """Test all_server() when there is some servers already stored."""
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
    """Test all_server() when there is some default servers already stored."""
    add_master_servers(dgraph, list(DEFAULT_MASTER_SERVERS_ADDRESS))

    response = rpc.all_servers.run(dgraph)
    assert response.game_servers_address == []
    assert set(response.master_servers_address) == DEFAULT_MASTER_SERVERS_ADDRESS
