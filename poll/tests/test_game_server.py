"""Test master_server.py."""

import pytest
from game_server import GameServer


def packet_type(packet):
    """Find the type of the given packet."""
    return bytes(packet)[10:14]


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
