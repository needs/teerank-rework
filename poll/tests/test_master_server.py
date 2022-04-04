"""Test master_server.py."""

from socket import AF_INET, AF_INET6, inet_pton

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
    return MasterServer("test-master-server:8300", server_pool)


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


def test_master_server_no_server(master_server, server_pool, update_stub):
    """Test when master server answer with no servers."""
    master_server.start_polling()

    packet = Packet()
    packet.pack_bytes(bytearray(b"\x00" * 10))
    packet.pack_bytes(bytearray(b"lis2"))

    master_server.process_packet(packet)
    master_server.stop_polling(update_stub, None)

    assert server_pool.servers == []

    assert len(update_stub.down_requests) == 0
    assert len(update_stub.up_requests) == 1
    assert update_stub.up_requests[0].address == master_server.address


def test_master_server_one_server_ipv4(master_server, server_pool, update_stub):
    """Test when master server answer with one IPv4 server."""
    host = "127.0.0.255"
    port = 40211

    master_server.start_polling()

    packet = Packet()
    packet.pack_bytes(bytearray(b"\x00" * 10))
    packet.pack_bytes(bytearray(b"lis2"))

    packet.pack_bytes(bytearray(b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xff"))
    packet.pack_bytes(inet_pton(AF_INET, host))
    packet.pack_bytes(port.to_bytes(2, byteorder="big"))

    master_server.process_packet(packet)
    master_server.stop_polling(update_stub, None)

    assert len(server_pool.servers) == 1
    assert server_pool.servers[0].address == f"{host}:{port}"

    assert len(update_stub.down_requests) == 0
    assert len(update_stub.up_requests) == 1
    assert update_stub.up_requests[0].address == master_server.address


def test_master_server_one_server_ipv6(master_server, server_pool, update_stub):
    """Test when master server answer with one IPv6 server."""
    host = "16e8:5e3a:e56e:b67c:17c:1561:6e5b:d116"
    port = 40211

    master_server.start_polling()

    packet = Packet()
    packet.pack_bytes(bytearray(b"\x00" * 10))
    packet.pack_bytes(bytearray(b"lis2"))

    packet.pack_bytes(inet_pton(AF_INET6, host))
    packet.pack_bytes(port.to_bytes(2, byteorder="big"))

    master_server.process_packet(packet)
    master_server.stop_polling(update_stub, None)

    assert len(server_pool.servers) == 1
    assert server_pool.servers[0].address == f"[{host}]:{port}"

    assert len(update_stub.down_requests) == 0
    assert len(update_stub.up_requests) == 1
    assert update_stub.up_requests[0].address == master_server.address
