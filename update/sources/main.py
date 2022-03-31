from concurrent import futures
import grpc
import update_pb2
import update_pb2_grpc

class UpdateServicer(update_pb2_grpc.UpdateServicer):
    def update(self, request, context):
        print(request.address)
        return update_pb2.google_dot_protobuf_dot_empty__pb2.Empty()


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    update_pb2_grpc.add_UpdateServicer_to_server(UpdateServicer(), server)

    server.add_insecure_port('update:8001')
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
