from concurrent import futures
import grpc
import database_pb2
import database_pb2_grpc

class DatabaseServicer(database_pb2_grpc.DatabaseServicer):
    def all_servers(self, request, context):
        return database_pb2.AllServersResponse(game_servers_addresse=[
        ], master_servers_addresse=[
            'master1.teeworlds.com:8300',
            'master2.teeworlds.com:8300',
            'master3.teeworlds.com:8300',
            'master4.teeworlds.com:8300'
        ])


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    database_pb2_grpc.add_DatabaseServicer_to_server(DatabaseServicer(), server)

    server.add_insecure_port('database:8003')
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
