"""Implement ServerPool class."""

import heapq
import logging
import random
import select
import time
from dataclasses import dataclass, field
from socket import gethostbyname
from urllib.parse import urlparse

from packet import Packet, PacketException
from server import Server


class ServerPool:
    """A list of servers to poll for data."""

    # Time between two poll for the same server.
    POLL_DELAY = 3 * 60

    # Maximum number of packet sent for each poll.
    MAX_PACKET_SENT_PER_POLL = 25

    # Number of poll failure after a server is removed.
    MAX_POLL_FAILURE = 3

    @dataclass(order=True)
    class _Entry:
        server: Server = field(compare=False)
        socket_address: tuple[str, int] = field(init=False, compare=False)
        poll_time: float = field(init=False)
        poll_failure: int = 0

        def __post_init__(self):
            """Finalize initialization."""
            # Randomize poll delay so that servers are evenly spread for polling,
            # and that should decrease packet loss even further.
            self.poll_time = time.time() + random.randrange(ServerPool.POLL_DELAY)

            # Extract server socket address.
            url = urlparse("//" + self.server.address)

            self.socket_address = (
                gethostbyname(url.hostname),
                url.port if url.port else 8300,
            )

    def __init__(self, socket):
        """Initialize a server pool."""
        self._entries = []
        self._servers = {}
        self._batch = {}
        self._socket = socket

    def add(self, server: Server) -> None:
        """Add the given server to the pool."""
        if server.address not in self._servers:
            logging.info("Adding server %s", server)
            heapq.heappush(self._entries, ServerPool._Entry(server))
            self._servers[server.address] = server

    def poll(self, update_stub, rank_stub) -> None:
        """Poll servers."""
        current_time = time.time()

        # Process any incoming packets.

        while select.select([self._socket], [], [], 0)[0]:

            data, socket_address = self._socket.recvfrom(4096)
            entry = self._batch.get(socket_address, None)

            if entry is not None:
                try:
                    entry.server.process_packet(Packet(data))
                except PacketException as exception:
                    logging.info(
                        "Server %s: Dropping packet: %s", entry.server, exception
                    )

        # Stop polling for the current batch and re-schedule servers.

        for entry in self._batch.values():
            if entry.server.stop_polling(update_stub, rank_stub):
                entry.poll_time += ServerPool.POLL_DELAY
                entry.poll_failure = 0

            else:
                entry.poll_failure += 1

                if entry.poll_failure == ServerPool.MAX_POLL_FAILURE:
                    logging.info("Removing server %s", entry.server)
                    if entry.server.address in self._servers:
                        del self._servers[entry.server.address]
                    continue

            heapq.heappush(self._entries, entry)

        self._batch = {}

        # Poll any server in the queue that have their poll timer exhausted.
        # Limit the number of packet sent to limit the number of packet loss.

        packet_count = 0

        while self._entries:
            if self._entries[0].poll_time > current_time:
                break
            if packet_count >= ServerPool.MAX_PACKET_SENT_PER_POLL:
                break

            entry = heapq.heappop(self._entries)
            server = entry.server
            packets = server.start_polling()

            for packet in packets:
                self._socket.sendto(bytes(packet), entry.socket_address)

            self._batch[entry.socket_address] = entry
            packet_count += len(packets)