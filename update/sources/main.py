"""Launch update service."""

from concurrent import futures

import grpc
import update_pb2
import update_pb2_grpc


class UpdateServicer(update_pb2_grpc.UpdateServicer):
    """gRPC update servicer implementation."""

    def update(self, request, context):
        """Update the given server."""
        print(request.address)
        return update_pb2.google_dot_protobuf_dot_empty__pb2.Empty()


def serve():
    """Start gRPC server."""
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    update_pb2_grpc.add_UpdateServicer_to_server(UpdateServicer(), server)

    server.add_insecure_port("update:8001")
    server.start()
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
