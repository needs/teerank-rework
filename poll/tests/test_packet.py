"""Test Packet."""

from packet import Packet


def test_packet_string():
    """Test Packet string handling."""
    strings = ["foo", "bar", "90", "null", "", "baz"]

    packet = Packet()

    for string in strings:
        packet.pack(string)
    for string in strings:
        assert packet.unpack() == string


def test_packet_int():
    """Test Packet integer handling."""
    integers = [10, 0, -1, -10, 40]

    packet = Packet()

    for integer in integers:
        packet.pack_int(integer)
    for integer in integers:
        assert packet.unpack_int() == integer


def test_packet_bytes():
    """Test Packet bytes handling."""
    datas = [b"\x01\x02", b"\x00", b"\xff\xff\xff", b"foobar\x00"]

    packet = Packet()

    for data in datas:
        packet.pack_bytes(data)
    for data in datas:
        assert packet.unpack_bytes(len(data)) == data


def test_packet_all():
    """Test Packet with all kind of data."""
    datas = [
        b"\x01\x02",
        "",
        50,
        -1,
        b"\x00",
        0,
        "foobar",
        b"\xff\xff\xff",
        "foobar",
        b"foobar\x00",
    ]

    packet = Packet()

    for data in datas:
        if isinstance(data, bytes):
            packet.pack_bytes(data)
        elif isinstance(data, str):
            packet.pack(data)
        elif isinstance(data, int):
            packet.pack_int(data)

    for data in datas:
        if isinstance(data, bytes):
            assert packet.unpack_bytes(len(data)) == data
        elif isinstance(data, str):
            assert packet.unpack() == data
        elif isinstance(data, int):
            assert packet.unpack_int() == data
