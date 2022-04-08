"""Query all game servers and master servers."""

import datetime

from gql import gql

DEFAULT_MASTER_SERVERS_ADDRESS = {
    "master1.teeworlds.com:8300",
    "master2.teeworlds.com:8300",
    "master3.teeworlds.com:8300",
    "master4.teeworlds.com:8300",
}


def add_master_servers(dgraph, addresses):
    """Add master servers."""
    if not addresses:
        return

    down_since = datetime.datetime.min.isoformat()

    dgraph.execute(
        gql(
            """
            mutation($master_servers: [AddMasterServerInput!]!) {
                addMasterServer(input: $master_servers) {
                    numUids
                }
            }
            """
        ),
        {
            "master_servers": [
                {
                    "address": address,
                    "downSince": down_since,
                }
                for address in addresses
            ]
        },
    )


def all_servers(dgraph) -> tuple[list[str], list[str]]:
    """Query all game servers and master servers."""
    query = dgraph.execute(
        gql(
            """
            query {
                queryGameServer {
                    address
                }
                queryMasterServer {
                    address
                }
            }
            """
        )
    )

    master_servers_address = {s["address"] for s in query["queryMasterServer"]}
    add_master_servers(dgraph, DEFAULT_MASTER_SERVERS_ADDRESS - master_servers_address)

    return (
        list(master_servers_address | DEFAULT_MASTER_SERVERS_ADDRESS),
        [game_server["address"] for game_server in query["queryGameServer"]],
    )
