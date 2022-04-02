"""Launch database service."""

from concurrent import futures

import database_pb2_grpc
import grpc
import rpc.all_servers
from dgraph import Dgraph


class DatabaseServicer(database_pb2_grpc.DatabaseServicer):
    """gRPC database servicer implementation."""

    def __init__(self, dgraph: Dgraph):
        """Initialize servicer."""
        self._dgraph = dgraph

    def all_servers(self, _request, _context):
        """Query all servers."""
        return rpc.all_servers.run(self._dgraph)


def serve(dgraph: Dgraph) -> None:
    """Start gRPC server."""
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    database_pb2_grpc.add_DatabaseServicer_to_server(DatabaseServicer(dgraph), server)

    server.add_insecure_port("database:8003")
    server.start()
    server.wait_for_termination()


if __name__ == "__main__":
    serve(Dgraph())
