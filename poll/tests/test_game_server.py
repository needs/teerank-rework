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


@pytest.fixture(name="client1")
def fixture_client1():
    """Return game server client."""
    return {
        "name": "test-client-1",
        "clan": "test-clan-1",
        "country": 0,
        "score": 1,
        "ingame": 1,
    }


@pytest.fixture(name="client2")
def fixture_client2():
    """Return game server client."""
    return {
        "name": "test-client-2",
        "clan": "test-clan-2",
        "country": 1,
        "score": 2,
        "ingame": 1,
    }


@pytest.fixture(name="game_server")
def fixture_game_server():
    """Create a game server for testing."""
    return GameServer("test-game-server:8300")


@pytest.fixture(name="is_up")
def fixture_is_up(game_server, rank_stub, update_stub):
    """Return a function checking if the game server is up."""

    def is_up():
        return (
            len(update_stub.game_up_requests) == 1
            and len(update_stub.game_down_requests) == 0
            and update_stub.game_up_requests[0].address == game_server.address
            and len(rank_stub.rank_requests) == 1
            and rank_stub.rank_requests[0].address == game_server.address
        )

    return is_up


def test_game_server_start_polling(game_server):
    """Test start_polling()."""
    packets = game_server.start_polling()

    assert len(packets) == 2
    assert packet_type(packets[0]) == b"gie3"
    assert packet_type(packets[1]) == b"fstd"


def test_game_server_vanilla(game_server, update_stub, rank_stub, is_up):
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

    assert is_up()


def test_game_server_legacy_64(game_server, update_stub, rank_stub, is_up):
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

    assert is_up()


def pack_client_extended(packet: Packet, client: dict) -> None:
    """Pack the given client in the packet with the extended format."""
    packet.pack(client["name"])
    packet.pack(client["clan"])
    packet.pack_int(client["country"])  # Country
    packet.pack_int(client["score"])  # Score
    packet.pack_int(client["ingame"])  # Ingame
    packet.pack("reserved")


def game_info_extended_packet(game_server: GameServer, num_clients: int):
    """Create a game info packet with the extended format."""
    packet = game_info_packet_header(game_server, b"iext")

    packet.pack("0.0.6")
    packet.pack("test-server")
    packet.pack("test-map")
    packet.pack_int(0)  # Map CRC.
    packet.pack_int(0)  # Map size.
    packet.pack("test-gametype")
    packet.pack_int(0)  # Flags
    packet.pack_int(num_clients)  # Number of players.
    packet.pack_int(16)  # Maximum number of players.
    packet.pack_int(num_clients)  # Number of clients.
    packet.pack_int(16)  # Maximum number of clients.

    packet.pack("reserved")  # Extra data.

    return packet


def test_game_server_extended(game_server, update_stub, rank_stub, client1, is_up):
    """Test sending an extended packet."""
    game_server.start_polling()

    packet = game_info_extended_packet(game_server, 1)
    pack_client_extended(packet, client1)

    game_server.process_packet(packet)
    game_server.stop_polling(update_stub, rank_stub)

    assert is_up()

    assert len(update_stub.game_up_requests[0].clients) == 1
    assert update_stub.game_up_requests[0].clients[0].name == client1["name"]


def test_game_server_extended_more(
    game_server, update_stub, rank_stub, client1, client2, is_up
):
    """Test sending an extended packet."""
    game_server.start_polling()

    packet = game_info_extended_packet(game_server, 2)
    pack_client_extended(packet, client1)

    game_server.process_packet(packet)

    packet = game_info_packet_header(game_server, b"iex+")
    packet.pack_int(0)  # Packet number
    packet.pack("reserved")  # Reserved
    pack_client_extended(packet, client2)
    game_server.process_packet(packet)

    game_server.stop_polling(update_stub, rank_stub)

    assert is_up()

    assert len(update_stub.game_up_requests[0].clients) == 2
    assert update_stub.game_up_requests[0].clients[0].name == client1["name"]
    assert update_stub.game_up_requests[0].clients[1].name == client2["name"]

    assert len(rank_stub.rank_requests[0].clients) == 2
    assert rank_stub.rank_requests[0].clients[0].name == client1["name"]
    assert rank_stub.rank_requests[0].clients[1].name == client2["name"]
