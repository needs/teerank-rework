"""
Implement GameServer, GameServerState and GameServerType classes.
"""

import secrets

from shared.game_server import GameServer as DatabaseGameServer, GameServerState, GameServerType
from shared.database import key_from_string

from backend.packet import Packet, PacketException
from backend.rank import rank


class GameServer(DatabaseGameServer):
    """
    Teeworld game server.
    """

    def __init__(self, key: str):
        """
        Initialize game server with the given key.
        """

        super().__init__(key)

        self._state_new = None
        self._request_token = None


    def _request_info_packet(self, request: bytes):
        """
        Create a 'request info' packet with the given request.
        """

        token = self._request_token[0:1]
        extra_token = self._request_token[1:3]

        packet = Packet()

        packet.pack_bytes(b'xe') # Magic header (2 bytes)
        packet.pack_bytes(extra_token) # Extra token (2 bytes)
        packet.pack_bytes(b'\x00\x00') # Reserved (2 bytes)
        packet.pack_bytes(b'\xff\xff\xff\xff') # Padding (4 bytes)
        packet.pack_bytes(request[0:4]) # Vanilla request (4 bytes)
        packet.pack_bytes(token) # Token (1 byte)

        return packet


    def start_polling(self) -> list[Packet]:
        """
        Setup internal state so that incoming data can be received.
        """

        # Generate a new request token.

        if self.state.server_type == GameServerType.EXTENDED:
            self._request_token = secrets.token_bytes(3)
        else:
            self._request_token = secrets.token_bytes(1) + bytes(2)

        # Pick a packet according to server type or send both packets if server
        # type is unknown.
        #
        # The packet is the same for both vanilla and extended servers, thanks
        # to a clever trick with the token field.

        packets = []

        if self.state.server_type in (GameServerType.UNKNOWN, \
                                      GameServerType.VANILLA, \
                                      GameServerType.EXTENDED):
            packets.append(self._request_info_packet(b'gie3'))
        if self.state.server_type in (GameServerType.UNKNOWN, \
                                      GameServerType.LEGACY_64):
            packets.append(self._request_info_packet(b'fstd'))

        # Reset _state_new.

        self._state_new = GameServerState(GameServerType.UNKNOWN)

        return packets


    def stop_polling(self) -> bool:
        """
        Check any received data and process them.
        """

        # Try to use extended data first because they are considered to be the
        # most superior format. Then use legacy 64 data because they provides
        # more information than the vanilla format.
        #
        # Check that data is complete by comparing the number of clients on the
        # server to the number of clients received.

        if not self._state_new.is_complete():
            return False

        # Now that the server is fully updated, save its state.

        old_state = self.state
        self.state = self._state_new
        self._state_new = None
        self.save()

        # Rank players after saving server so that player already exist in the
        # database.

        rank(old_state, self.state)

        return True


    def process_packet(self, packet: Packet) -> None:
        """
        Process packet header and route the packet to its final process
        function.
        """

        packet.unpack_bytes(10) # Padding
        packet_type = packet.unpack_bytes(4)

        # Servers send token back as an integer that is a combination of token
        # and extra_token fields of the packet we sent.  However the received
        # token has some its byte mixed because of endianess and we need to swap
        # some bytes to get the full token back.

        token = packet.unpack_int().to_bytes(3, byteorder='big')
        token = bytes([token[2], token[0], token[1]])

        if token != self._request_token:
            raise PacketException('Wrong request token.')

        if packet_type == b'inf3':
            state = self._process_packet_vanilla(packet)
        elif packet_type == b'dtsf':
            state = self._process_packet_legacy_64(packet)
        elif packet_type == b'iext':
            state = self._process_packet_extended(packet)
        elif packet_type == b'iex+':
            state = self._process_packet_extended_more(packet)

        else:
            raise PacketException('Packet type not supported.')

        self._state_new.merge(state)


    @staticmethod
    def _process_packet_vanilla(packet: Packet) -> GameServerState:
        """
        Parse the default response of the vanilla client.
        """

        state = GameServerState(GameServerType.VANILLA)

        state.info = {
            'version': packet.unpack(),
            'name': packet.unpack(),
            'map_name': packet.unpack(),
            'game_type': packet.unpack(),
            'flags': packet.unpack_int(),
            'num_players': packet.unpack_int(),
            'max_players': packet.unpack_int(),
            'num_clients': packet.unpack_int(),
            'max_clients': packet.unpack_int()
        }

        while packet.unpack_remaining() >= 5:
            key = key_from_string(packet.unpack())
            state.clients[key] = {
                'clan': packet.unpack(),
                'country': packet.unpack_int(),
                'score': packet.unpack_int(),
                'ingame': bool(packet.unpack_int())
            }

        return state


    @staticmethod
    def _process_packet_legacy_64(packet: Packet) -> GameServerState:
        """
        Parse legacy 64 packet.
        """

        state = GameServerState(GameServerType.LEGACY_64)

        state.info = {
            'version': packet.unpack(),
            'name': packet.unpack(),
            'map_name': packet.unpack(),
            'game_type': packet.unpack(),
            'flags': packet.unpack_int(),
            'num_players': packet.unpack_int(),
            'max_players': packet.unpack_int(),
            'num_clients': packet.unpack_int(),
            'max_clients': packet.unpack_int()
        }

        # Even though the offset is advertised as an integer, in real condition
        # we receive a single byte.

        packet.unpack_bytes(1) # Offset

        while packet.unpack_remaining() >= 5:
            key = key_from_string(packet.unpack())
            state.clients[key] = {
                'clan': packet.unpack(),
                'country': packet.unpack_int(),
                'score': packet.unpack_int(),
                'ingame': bool(packet.unpack_int())
            }

        return state


    @staticmethod
    def _process_packet_extended(packet: Packet) -> GameServerState:
        """
        Parse the extended server info packet.
        """

        state = GameServerState(GameServerType.EXTENDED)

        state.info = {
            'version': packet.unpack(),
            'name': packet.unpack(),
            'map_name': packet.unpack(),
            'map_crc': packet.unpack_int(),
            'map_size': packet.unpack_int(),
            'game_type': packet.unpack(),
            'flags': packet.unpack_int(),
            'num_players': packet.unpack_int(),
            'max_players': packet.unpack_int(),
            'num_clients': packet.unpack_int(),
            'max_clients': packet.unpack_int()
        }

        packet.unpack() # Reserved

        while packet.unpack_remaining() >= 6:
            key = key_from_string(packet.unpack())
            state.clients[key] = {
                'clan': packet.unpack(),
                'country': packet.unpack_int(-1),
                'score': packet.unpack_int(),
                'ingame': bool(packet.unpack_int())
            }
            packet.unpack() # Reserved

        return state


    @staticmethod
    def _process_packet_extended_more(packet: Packet) -> GameServerState:
        """
        Parse the extended server info packet.
        """

        state = GameServerState(GameServerType.EXTENDED)

        packet.unpack_int() # Packet number
        packet.unpack() # Reserved

        while packet.unpack_remaining() >= 6:
            key = key_from_string(packet.unpack())
            state.clients[key] = {
                'clan': packet.unpack(),
                'country': packet.unpack_int(-1),
                'score': packet.unpack_int(),
                'ingame': bool(packet.unpack_int())
            }
            packet.unpack() # Reserved

        return state
