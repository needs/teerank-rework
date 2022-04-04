"""Launch poll service."""

from socket import AF_INET, SOCK_DGRAM, gethostname
from socket import socket as Socket
from time import sleep

import database_pb2_grpc
import google.protobuf.empty_pb2
import grpc
import rank_pb2_grpc
import update_pb2_grpc
from game_server import GameServer
from master_server import MasterServer
from server_pool import ServerPool

if __name__ == "__main__":
    update_stub = update_pb2_grpc.UpdateStub(grpc.insecure_channel("update:8001"))
    rank_stub = rank_pb2_grpc.RankStub(grpc.insecure_channel("rank:8002"))
    database_stub = database_pb2_grpc.DatabaseStub(
        grpc.insecure_channel("database:8003")
    )

    # Bind socket to a specific port to be able to tell docker which port to
    # expose in order to receive packets.
    socket = Socket(family=AF_INET, type=SOCK_DGRAM)
    socket.bind((gethostname(), 8000))

    server_pool = ServerPool(socket)

    response = database_stub.all_servers(google.protobuf.empty_pb2.Empty())

    for address in response.master_servers_address:
        server_pool.add(MasterServer(address, server_pool))
    for address in response.game_servers_address:
        server_pool.add(GameServer(address))

    while True:
        server_pool.poll(rank_stub, update_stub)
        sleep(1)
