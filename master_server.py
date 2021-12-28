import socket

from server import Server
from packet import Packet
from server_pool import server_pool
from game_server import GameServer

class MasterServer(Server):
    def __init__(self, hostname: str):
        self.hostname = hostname
        super().__init__(socket.gethostbyname(hostname), 8300)


    def load(self) -> None:
        # self.data = json.loads(redis.get(self.redis_key))
        self.data = {}


    def save(self) -> None:
        # redis.set(self.redis_key, json.dumps(self.data))
        pass


    def start_polling(self) -> list[Packet]:
        self._packet_count = 0
        return [Packet(packet_type=b'\xff\xff\xff\xffreq2')]


    def stop_polling(self) -> bool:
        # There is no reliable way to know when all packets have been received.
        # Therefor when at least one packet have been received, we considere
        # that the polling was a success and we move on.

        return self._packet_count > 0


    def process_packet(self, packet: Packet) -> None:
        if packet.type == b'\xff\xff\xff\xfflis2':

            while len(packet) >= 18:
                data = packet.unpack_bytes(16)

                if data[:12] == b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xff':
                    ip = socket.inet_ntop(socket.AF_INET, data[12:16])
                else:
                    ip = '[' + socket.inet_ntop(socket.AF_INET6, data[:16]) + ']'

                port = int.from_bytes(packet.unpack_bytes(2), byteorder='big')

                if not (ip == self.ip and port == self.port):
                    if (ip, port) not in server_pool:
                        server_pool.add(GameServer(ip, port))

            self._packet_count += 1


def load_master_servers() -> list[MasterServer]:
    """Load all master servers stored in the database."""

    # hostnames = redis.smembers('master-servers')
    hostnames = None
    hostname = None

    if hostnames is None:
        hostnames = [
            'master1.teeworlds.com',
            'master2.teeworlds.com',
            'master3.teeworlds.com',
            'master4.teeworlds.com'
        ]

        # redis.sadd('master-servers', *hostnames)

    master_servers = []

    for hostname in hostnames:
        master_server = MasterServer(hostname)
        master_server.load()
        master_servers.append(master_server)

    return master_servers
