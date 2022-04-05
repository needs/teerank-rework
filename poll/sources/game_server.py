"""Implement operations on game server."""

import secrets
from enum import IntEnum

import rank_pb2
import update_pb2
from packet import Packet, PacketException
from server import Server


class GameServerType(IntEnum):
    """Game server network format."""

    UNKNOWN = -1
    VANILLA = 0
    LEGACY_64 = 1
    EXTENDED = 2


class GameServer(Server):
    """Operation on Teeworld game server."""

    _state: dict

    def __init__(self, address: str):
        """Initialize game server with the given address."""
        super().__init__(address)

        self._state = {}

    def _request_info_packet(self, request: bytes):
        """Create a 'request info' packet with the given request."""
        token = self._request_token[0:1]
        extra_token = self._request_token[1:3]

        packet = Packet()

        packet.pack_bytes(b"xe")  # Magic header (2 bytes)
        packet.pack_bytes(extra_token)  # Extra token (2 bytes)
        packet.pack_bytes(b"\x00\x00")  # Reserved (2 bytes)
        packet.pack_bytes(b"\xff\xff\xff\xff")  # Padding (4 bytes)
        packet.pack_bytes(request[0:4])  # Vanilla request (4 bytes)
        packet.pack_bytes(token)  # Token (1 byte)

        return packet

    def start_polling(self) -> list[Packet]:
        """Prepare polling."""
        server_type = self._state.get("type", GameServerType.UNKNOWN)

        # Generate a new request token.

        if server_type == GameServerType.EXTENDED:
            self._request_token = secrets.token_bytes(3)
        else:
            self._request_token = secrets.token_bytes(1) + bytes(2)

        # Pick a packet according to server type or send both packets if server
        # type is unknown.
        #
        # The packet is the same for both vanilla and extended servers, thanks
        # to a clever trick with the token field.

        packets = []

        if server_type in (
            GameServerType.UNKNOWN,
            GameServerType.VANILLA,
            GameServerType.EXTENDED,
        ):
            packets.append(self._request_info_packet(b"gie3"))
        if server_type in (GameServerType.UNKNOWN, GameServerType.LEGACY_64):
            packets.append(self._request_info_packet(b"fstd"))

        # Reset server state.

        self._state = {}

        return packets

    def stop_polling(self, update_stub, rank_stub) -> bool:
        """Check any received data and process them."""
        if not self._state:
            update_stub.game_server_down(
                update_pb2.GameServerDownRequest(address=self.address)
            )
            return False

        # Check that data is complete by comparing the number of clients
        # received against the number of clients advertised.

        if self._state.get("numClients", -1) != len(self._state.get("clients", [])):
            return False

        update_stub.game_server_up(
            update_pb2.GameServerUpRequest(
                address=self.address,
                version=self._state["version"],
                name=self._state["name"],
                gametype=self._state["gameType"],
                map=self._state["map"],
                max_clients=self._state["maxClients"],
                max_players=self._state["maxPlayers"],
                clients=[
                    update_pb2.GameServerUpRequest.Client(
                        name=client["name"],
                        clan=client["clan"],
                        country=client["country"],
                        score=client["score"],
                        ingame=client["ingame"],
                    )
                    for client in self._state["clients"]
                ],
            )
        )

        rank_stub.rank(
            rank_pb2.RankRequest(
                address=self.address,
                gametype=self._state["gameType"],
                map=self._state["map"],
                clients=[
                    rank_pb2.RankRequest.Client(
                        name=client["name"],
                        clan=client["clan"],
                        country=client["country"],
                        score=client["score"],
                        ingame=client["ingame"],
                    )
                    for client in self._state["clients"]
                ],
            )
        )

        return True

    def process_packet(self, packet: Packet) -> None:
        """Process packet header and route the packet content."""
        packet.unpack_bytes(10)  # Padding
        packet_type_bytes = packet.unpack_bytes(4)

        # Check packet type.

        if packet_type_bytes == b"inf3":
            packet_type = GameServerType.VANILLA
            unpack = GameServer._process_packet_vanilla
        elif packet_type_bytes == b"dtsf":
            packet_type = GameServerType.LEGACY_64
            unpack = GameServer._process_packet_legacy_64
        elif packet_type_bytes == b"iext":
            packet_type = GameServerType.EXTENDED
            unpack = GameServer._process_packet_extended
        elif packet_type_bytes == b"iex+":
            packet_type = GameServerType.EXTENDED
            unpack = GameServer._process_packet_extended_more
        else:
            raise PacketException("Packet type not supported.")

        # Servers send token back as an integer that is a combination of token
        # and extra_token fields of the packet we sent.  However the received
        # token has some its byte mixed because of endianess and we need to swap
        # some bytes to get the full token back.

        token = packet.unpack_int().to_bytes(3, byteorder="big")
        token = bytes([token[2], token[0], token[1]])

        if token != self._request_token:
            raise PacketException("Wrong request token.")

        # Merge received state into the new state.  This step is required
        # because new state can be received in many smaller parts.

        state_type = self._state.get("type", GameServerType.UNKNOWN)

        if packet_type >= state_type:
            state = unpack(packet)

            if packet_type == state_type:
                # Merge extended state, otherwise replace.
                if packet_type == GameServerType.EXTENDED:
                    state["clients"] = self._state.get("clients", []) + state["clients"]
                    self._state |= state
                else:
                    self._state = state

            elif packet_type > state_type:
                # Replace old state with the new one.
                self._state = state

    @staticmethod
    def _process_packet_vanilla(packet: Packet) -> dict:
        """Parse the default response of the vanilla client."""
        state: dict = {}

        state["type"] = GameServerType.VANILLA
        state["version"] = packet.unpack()
        state["name"] = packet.unpack()
        state["map"] = packet.unpack()
        state["gameType"] = packet.unpack()
        packet.unpack_int()  # Flags
        state["numPlayers"] = packet.unpack_int()
        state["maxPlayers"] = packet.unpack_int()
        state["numClients"] = packet.unpack_int()
        state["maxClients"] = packet.unpack_int()

        state["clients"] = []

        while packet.unpack_remaining() >= 5:
            state["clients"].append(
                {
                    "name": packet.unpack(),
                    "clan": packet.unpack(),
                    "country": packet.unpack_int(),
                    "score": packet.unpack_int(),
                    "ingame": bool(packet.unpack_int()),
                }
            )

        return state

    @staticmethod
    def _process_packet_legacy_64(packet: Packet) -> dict:
        """Parse legacy 64 packet."""
        state: dict = {}

        state["type"] = GameServerType.LEGACY_64
        state["version"] = packet.unpack()
        state["name"] = packet.unpack()
        state["map"] = packet.unpack()
        state["gameType"] = packet.unpack()
        packet.unpack_int()  # Flags
        state["numPlayers"] = packet.unpack_int()
        state["maxPlayers"] = packet.unpack_int()
        state["numClients"] = packet.unpack_int()
        state["maxClients"] = packet.unpack_int()

        state["clients"] = []

        # Even though the offset is advertised as an integer, in real condition
        # we receive a single byte.

        packet.unpack_bytes(1)  # Offset

        while packet.unpack_remaining() >= 5:
            state["clients"].append(
                {
                    "name": packet.unpack(),
                    "clan": packet.unpack(),
                    "country": packet.unpack_int(),
                    "score": packet.unpack_int(),
                    "ingame": bool(packet.unpack_int()),
                }
            )

        return state

    @staticmethod
    def _process_packet_extended(packet: Packet) -> dict:
        """Parse the extended server info packet."""
        state: dict = {}

        state["type"] = GameServerType.EXTENDED
        state["version"] = packet.unpack()
        state["name"] = packet.unpack()
        state["map"] = packet.unpack()
        packet.unpack_int()  # Map CRC
        packet.unpack_int()  # Map size
        state["gameType"] = packet.unpack()
        packet.unpack_int()  # Flags
        state["numPlayers"] = packet.unpack_int()
        state["maxPlayers"] = packet.unpack_int()
        state["numClients"] = packet.unpack_int()
        state["maxClients"] = packet.unpack_int()

        state["clients"] = []

        packet.unpack()  # Reserved

        while packet.unpack_remaining() >= 6:
            state["clients"].append(
                {
                    "name": packet.unpack(),
                    "clan": packet.unpack(),
                    "country": packet.unpack_int(),
                    "score": packet.unpack_int(),
                    "ingame": bool(packet.unpack_int()),
                }
            )
            packet.unpack()  # Reserved

        return state

    @staticmethod
    def _process_packet_extended_more(packet: Packet) -> dict:
        """Parse the extended server info packet."""
        state: dict = {"type": GameServerType.EXTENDED, "clients": []}

        packet.unpack_int()  # Packet number
        packet.unpack()  # Reserved

        while packet.unpack_remaining() >= 6:
            state["clients"].append(
                {
                    "name": packet.unpack(),
                    "clan": packet.unpack(),
                    "country": packet.unpack_int(),
                    "score": packet.unpack_int(),
                    "ingame": bool(packet.unpack_int()),
                }
            )
            packet.unpack()  # Reserved

        return state
