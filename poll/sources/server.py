"""Implement Server class."""

from dataclasses import dataclass


@dataclass
class Server:
    """Server class."""

    address: str

    def __str__(self):
        """Server address."""
        return self.address
