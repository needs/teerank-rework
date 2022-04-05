"""Test master_server.py."""

import pytest
from game_server import GameServer
from packet import Packet


def packet_type(packet):
    """Find the type of the given packet."""
    return bytes(packet)[10:14]


def game_info_packet_header(game_server: GameServer, packet_type: bytes) -> Packet:
    """Pack header of any game info packet with the given type."""
    packet = Packet()

    packet.pack_bytes(b"\x00" * 10)
    packet.pack_bytes(bytearray(packet_type))

    token = game_server._request_token[0:3]
    token = bytes([token[1], token[2], token[0]])
    packet.pack_int(int.from_bytes(token, byteorder="big"))

    return packet


@pytest.fixture(name="game_server")
def fixture_game_server():
    """Create a game server for testing."""
    return GameServer("test-game-server:8300")


def test_game_server_start_polling(game_server):
    """Test start_polling()."""
    packets = game_server.start_polling()

    assert len(packets) == 2
    assert packet_type(packets[0]) == b"gie3"
    assert packet_type(packets[1]) == b"fstd"


def test_game_server_vanilla(game_server, update_stub, rank_stub):
    """Test sending a vanilla packet."""
    game_server.start_polling()

    packet = game_info_packet_header(game_server, b"inf3")

    packet.pack("0.0.6")
    packet.pack("test-server")
    packet.pack("test-map")
    packet.pack("test-gametype")
    packet.pack_int(0)  # Flags
    packet.pack_int(1)  # Number of players.
    packet.pack_int(16)  # Maximum number of players.
    packet.pack_int(1)  # Number of clients.
    packet.pack_int(16)  # Maximum number of clients.

    packet.pack("test-player-1")
    packet.pack("test-clan-1")
    packet.pack_int(1)  # Country
    packet.pack_int(2)  # Score
    packet.pack_int(1)  # Ingame

    game_server.process_packet(packet)
    game_server.stop_polling(update_stub, rank_stub)

    assert len(update_stub.game_up_requests) == 1
    assert len(update_stub.game_down_requests) == 0
    assert update_stub.game_up_requests[0].address == game_server.address

    assert len(rank_stub.rank_requests) == 1
    assert rank_stub.rank_requests[0].address == game_server.address


def test_game_server_legacy_64(game_server, update_stub, rank_stub):
    """Test sending a legacy 64 packet."""
    game_server.start_polling()

    packet = game_info_packet_header(game_server, b"dtsf")

    packet.pack("0.0.6")
    packet.pack("test-server")
    packet.pack("test-map")
    packet.pack("test-gametype")
    packet.pack_int(0)  # Flags
    packet.pack_int(1)  # Number of players.
    packet.pack_int(16)  # Maximum number of players.
    packet.pack_int(1)  # Number of clients.
    packet.pack_int(16)  # Maximum number of clients.

    packet.pack_bytes(b"\x00")  # Extra data.

    packet.pack("test-player-1")
    packet.pack("test-clan-1")
    packet.pack_int(1)  # Country
    packet.pack_int(2)  # Score
    packet.pack_int(1)  # Ingame

    game_server.process_packet(packet)
    game_server.stop_polling(update_stub, rank_stub)

    assert len(update_stub.game_up_requests) == 1
    assert len(update_stub.game_down_requests) == 0
    assert update_stub.game_up_requests[0].address == game_server.address

    assert len(rank_stub.rank_requests) == 1
    assert rank_stub.rank_requests[0].address == game_server.address


def test_game_server_extended(game_server, update_stub, rank_stub):
    """Test sending an extended packet."""
    game_server.start_polling()

    packet = game_info_packet_header(game_server, b"iext")

    packet.pack("0.0.6")
    packet.pack("test-server")
    packet.pack("test-map")
    packet.pack_int(0)  # Map CRC.
    packet.pack_int(0)  # Map size.
    packet.pack("test-gametype")
    packet.pack_int(0)  # Flags
    packet.pack_int(1)  # Number of players.
    packet.pack_int(16)  # Maximum number of players.
    packet.pack_int(1)  # Number of clients.
    packet.pack_int(16)  # Maximum number of clients.

    packet.pack("reserved")  # Extra data.

    packet.pack("test-player-1")
    packet.pack("test-clan-1")
    packet.pack_int(1)  # Country
    packet.pack_int(2)  # Score
    packet.pack_int(1)  # Ingame
    packet.pack("reserved")

    game_server.process_packet(packet)
    game_server.stop_polling(update_stub, rank_stub)

    assert len(update_stub.game_up_requests) == 1
    assert len(update_stub.game_down_requests) == 0
    assert update_stub.game_up_requests[0].address == game_server.address

    assert len(rank_stub.rank_requests) == 1
    assert rank_stub.rank_requests[0].address == game_server.address
