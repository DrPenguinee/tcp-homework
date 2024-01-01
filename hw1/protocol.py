import socket
import random
from TCP_packet import TCP_packet
from Timeout import Timeout

class UDPBasedProtocol:
    def __init__(self, *, local_addr, remote_addr):
        self.udp_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.remote_addr = remote_addr
        self.udp_socket.bind(local_addr)

    def sendto(self, data: bytes):
        return self.udp_socket.sendto(data, self.remote_addr)

    def recvfrom(self, n) -> bytes:
        msg, addr = self.udp_socket.recvfrom(n)
        return msg

    def close(self):
        self.udp_socket.close()


class MyTCPProtocol(UDPBasedProtocol):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.seq_num = 0
        self.timeout = 0.0005

    def send(self, data: bytes, id: str):
        chunks = [data[i:i + TCP_packet.MSS] for i in range(0, len(data), TCP_packet.MSS)]
        for chunk in chunks:
            msg = TCP_packet(self.seq_num, self.seq_num, 0, 0, 0, chunk)
            raw_msg = msg.pack_segment()
            self.sendto(raw_msg)

        return len(data)

    def recv(self, n: int, id: str):
        chunks = [b''] * ((n // TCP_packet.MSS))
        data = b''.join(list(map(lambda x: x[1], sorted(chunks.items()))))
        return data[:n]
