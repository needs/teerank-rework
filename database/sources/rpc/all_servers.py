"""Implement "all_servers" RPC."""

import datetime

import database_pb2

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
        """
        mutation($master_servers: [AddMasterServerInput!]!) {
            addMasterServer(input: $master_servers) {
                numUids
            }
        }
        """,
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


def run(dgraph) -> database_pb2.AllServersResponse:
    """Implement "all_servers" RPC."""
    query = dgraph.execute(
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

    master_servers_address = {s["address"] for s in query["queryMasterServer"]}
    add_master_servers(dgraph, DEFAULT_MASTER_SERVERS_ADDRESS - master_servers_address)

    return database_pb2.AllServersResponse(
        game_servers_address=[s["address"] for s in query["queryGameServer"]],
        master_servers_address=master_servers_address | DEFAULT_MASTER_SERVERS_ADDRESS,
    )
