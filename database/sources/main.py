"""Launch database service."""

from concurrent import futures

import database_pb2_grpc
import grpc
import rpc.all_servers


class DatabaseServicer(database_pb2_grpc.DatabaseServicer):
    """gRPC database servicer implementation."""

    def all_servers(self, _request, _context):
        """Query all servers."""
        return rpc.all_servers.run()


def serve():
    """Start gRRPC server."""
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    database_pb2_grpc.add_DatabaseServicer_to_server(DatabaseServicer(), server)

    server.add_insecure_port("database:8003")
    server.start()
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
