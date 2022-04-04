"""Test master_server.py."""

from master_server import MasterServer
from packet import Packet


def test_master_server_start_polling():
    """Test start_polling()."""
    master_server = MasterServer("test-master-server:8300", None)

    packets = master_server.start_polling()

    expected_packet = Packet()
    expected_packet.pack_bytes(bytearray(b"\xff" * 10))
    expected_packet.pack_bytes(bytearray(b"req2"))

    assert len(packets) == 1
    assert bytes(packets[0]) == bytes(expected_packet)
