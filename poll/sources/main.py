from time import sleep
import grpc
import update_pb2_grpc
import update_pb2
import rank_pb2_grpc
import rank_pb2
import database_pb2_grpc
import database_pb2

if __name__ == '__main__':
    update_channel = grpc.insecure_channel('update:8001')
    rank_channel = grpc.insecure_channel('rank:8002')
    database_channel = grpc.insecure_channel('database:8003')

    update_stub = update_pb2_grpc.UpdateStub(update_channel)
    rank_stub = rank_pb2_grpc.RankStub(rank_channel)
    database_stub = database_pb2_grpc.DatabaseStub(database_channel)

    update_request = update_pb2.UpdateRequest(address='test-update-gameserver')
    rank_request = rank_pb2.RankRequest(address='test-rank-gameserver')

    while True:
        try:
            response = database_stub.all_servers(database_pb2.google_dot_protobuf_dot_empty__pb2.Empty())

            for master_server_address in response.master_servers_address:
                print(master_server_address)
            for game_server_address in response.game_servers_address:
                print(game_server_address)

        except Exception as e:
            print(e)

        try:
            update_stub.update(update_request)
        except Exception as e:
            print(e)

        try:
            rank_stub.rank(rank_request)
        except Exception as e:
            print(e)

        sleep(1)
