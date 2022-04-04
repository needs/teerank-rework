"""Implement class Packet and class PacketException."""


class PacketException(Exception):
    """Type for exception happening when processing packet."""


class Packet:
    """Pack and unpack data following the Teeworlds packet format."""

    def __init__(self, data: bytearray = None):
        """Initialize packet with the given data."""
        if data is None:
            data = bytearray()

        self._data = data

    def unpack_remaining(self) -> int:
        """Return the number of remaining unpack() call."""
        return self._data.count(b"\x00")

    def unpack(self) -> str:
        """Unpack string."""
        data, separator, self._data = self._data.partition(b"\x00")

        if separator != b"\x00":
            raise PacketException("Cannot unpack a string.")

        return data.decode("utf-8", "backslashreplace")

    def unpack_bytes(self, count: int) -> bytes:
        """Unpack bytes."""
        if len(self._data) < count:
            raise PacketException("Cannot unpack the required amount of bytes.")

        data = self._data[:count]
        self._data = self._data[count:]
        return data

    def unpack_int(self) -> int:
        """Unpack integer."""
        try:
            value = self.unpack()
            return -1 if value == "" else int(value)
        except ValueError as exception:
            raise PacketException("Cannot unpack an integer.") from exception

    def pack(self, string: str) -> None:
        """Pack string."""
        self._data.extend(string.encode("utf-8"))

    def pack_bytes(self, data: bytes) -> None:
        """Pack bytes."""
        self._data.extend(data)

    def __len__(self) -> int:
        """Packet data size (in bytes)."""
        return len(self._data)

    def __bytes__(self) -> bytes:
        """Packet data as bytes."""
        return bytes(self._data)
