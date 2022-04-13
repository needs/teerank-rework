"""Launch poll service."""

from http.client import HTTPConnection
from socket import AF_INET, SOCK_DGRAM, gethostname
from socket import socket as Socket
from time import sleep

import google.protobuf.empty_pb2
import grpc
import rank_pb2_grpc
import update_pb2_grpc
from all_servers import all_servers
from game_server import GameServer
from gql_client import GQLClient
from master_server import MasterServer
from server_pool import ServerPool

if __name__ == "__main__":
    update_stub = update_pb2_grpc.UpdateStub(grpc.insecure_channel("update:8001"))
    rank_stub = rank_pb2_grpc.RankStub(grpc.insecure_channel("rank:8002"))

    # Bind socket to a specific port to be able to tell docker which port to
    # expose in order to receive packets.
    socket = Socket(family=AF_INET, type=SOCK_DGRAM)
    socket.bind((gethostname(), 8000))

    server_pool = ServerPool(socket)

    client = GQLClient(HTTPConnection(url="graphql:8080"), "/graphql")
    master_servers_address, game_servers_address = all_servers(client)

    for address in master_servers_address:
        server_pool.add(MasterServer(address, server_pool))
    for address in game_servers_address:
        server_pool.add(GameServer(address))

    while True:
        server_pool.poll(rank_stub, update_stub)
        sleep(1)
