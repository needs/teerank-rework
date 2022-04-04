"""Implement MasterServer."""

import socket

import update_pb2
from game_server import GameServer
from packet import Packet
from server import Server
from server_pool import ServerPool


class MasterServer(Server):
    """Implement master server polling operations."""

    _game_servers_addresses: set[str]
    _is_up: bool

    def __init__(self, address: str, server_pool: ServerPool):
        """Initialize master server with the given address."""
        super().__init__(address)
        self._server_pool = server_pool

    def start_polling(self) -> list[Packet]:
        """Poll master server."""
        self._is_up = False
        self._game_servers_addresses = set()

        # 10 bytes of padding and the 'req2' packet type.
        return [Packet(bytearray(b"\xff\xff\xff\xff\xff\xff\xff\xff\xff\xffreq2"))]

    def stop_polling(self, update_stub, rank_stub) -> bool:
        """Stop master server polling."""
        # There is no reliable way to know when all packets have been received.
        # Therefor when at least one packet have been received, we considere
        # that the polling was a success and we move on.

        if not self._is_up:
            update_stub.master_server_down(
                update_pb2.MasterServerDownRequest(address=self.address)
            )
            return False

        update_stub.master_server_up(
            update_pb2.MasterServerUpRequest(
                address=self.address,
                game_servers_address=list(self._game_servers_addresses),
            )
        )
        return True

    def process_packet(self, packet: Packet) -> None:
        """
        Process master server packet.

        Add any game server not yet in the server pool.
        """
        self._is_up = True

        packet.unpack_bytes(10)  # Padding
        packet_type = packet.unpack_bytes(4)

        if packet_type == b"lis2":

            while len(packet) >= 18:
                data = packet.unpack_bytes(16)

                if data[:12] == b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xff":
                    host = socket.inet_ntop(socket.AF_INET, data[12:16])
                else:
                    host = "[" + socket.inet_ntop(socket.AF_INET6, data[:16]) + "]"

                port = str(int.from_bytes(packet.unpack_bytes(2), byteorder="big"))
                address = host + ":" + port

                if address != self.address and address not in self._server_pool:
                    self._server_pool.add(GameServer(address))

                self._game_servers_addresses.add(address)
