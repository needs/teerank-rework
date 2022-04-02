"""Test all_servers()."""

import rpc.all_servers


def test_all_servers(dgraph):
    """Test all_server() when there is no servers already stored."""
    response = rpc.all_servers.run(dgraph)

    assert response.game_servers_address == []
    assert response.master_servers_address == [
        "master1.teeworlds.com:8300",
        "master2.teeworlds.com:8300",
        "master3.teeworlds.com:8300",
        "master4.teeworlds.com:8300",
    ]
