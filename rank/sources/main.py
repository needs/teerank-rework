from concurrent import futures
import grpc
import rank_pb2
import rank_pb2_grpc

class RankServicer(rank_pb2_grpc.RankServicer):
    def rank(self, request, context):
        print(request.address)
        return rank_pb2.google_dot_protobuf_dot_empty__pb2.Empty()


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    rank_pb2_grpc.add_RankServicer_to_server(RankServicer(), server)

    server.add_insecure_port('rank:8002')
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
