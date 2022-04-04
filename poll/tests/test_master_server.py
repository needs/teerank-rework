"""Test master_server.py."""

import pytest
from master_server import MasterServer
from packet import Packet


@pytest.fixture(name="update_stub")
def fixture_update_stub():
    """Create a fake update stub for testing."""

    class UpdateStub:
        def __init__(self):
            self.up_requests = []
            self.down_requests = []

        def master_server_up(self, request):
            self.up_requests.append(request)

        def master_server_down(self, request):
            self.down_requests.append(request)

    return UpdateStub()


@pytest.fixture(name="server_pool")
def fixture_server_pool():
    """Create a fake server pool for testing."""

    class FakeServerPool:
        def __init__(self):
            self.servers = []

        def add(self, server):
            self.servers.append(server)

    return FakeServerPool()


@pytest.fixture(name="master_server")
def fixture_master_server(server_pool):
    """Create a master server for testing."""
    return MasterServer("test-master-server:8300", None)


def test_master_server_start_polling(master_server):
    """Test start_polling()."""
    packets = master_server.start_polling()

    expected_packet = Packet()
    expected_packet.pack_bytes(bytearray(b"\xff" * 10))
    expected_packet.pack_bytes(bytearray(b"req2"))

    assert len(packets) == 1
    assert bytes(packets[0]) == bytes(expected_packet)


def test_master_server_down(master_server, server_pool, update_stub):
    """Test when master server does not answer."""
    master_server.start_polling()
    master_server.stop_polling(update_stub, None)

    assert server_pool.servers == []

    assert len(update_stub.up_requests) == 0
    assert len(update_stub.down_requests) == 1
    assert update_stub.down_requests[0].address == master_server.address
