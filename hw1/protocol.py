import socket
import random
from TCP_packet import TCP_packet

ACK_TIMEOUT = 0.0001
FIN_TIMEOUT = ACK_TIMEOUT * 4


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


class MyTCPProtocol(UDPBasedProtocol):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.seq_num = random.randint(1, 100)

    def send(self, data: bytes, id: str):
        # print(id + " START SENDING")
        self.seq_num += 100

        syn = TCP_packet(self.seq_num, 0, 0, 1, 0, b'')
        raw_syn = syn.pack_segment()
        self.sendto(raw_syn)

        # awaiting SYN+ACK
        while True:
            try:
                self.udp_socket.settimeout(ACK_TIMEOUT)
                raw_synack = self.recvfrom(TCP_packet.PACKET_SIZE)
                synack = TCP_packet.unpack_segment(raw_synack)
                if synack.is_synack() and synack.ack_num == syn.seq_num + 1:
                    break
            except socket.timeout:
                self.sendto(raw_syn)

        self.seq_num += 1
        chunks = [data[i:i + TCP_packet.MSS] for i in range(0, len(data), TCP_packet.MSS)]
        for chunk in chunks:
            msg = TCP_packet(self.seq_num, self.seq_num, 0, 0, 0, chunk)
            raw_msg = msg.pack_segment()

            while True:
                self.sendto(raw_msg)

                try:
                    self.udp_socket.settimeout(ACK_TIMEOUT)
                    raw_ack = self.recvfrom(TCP_packet.PACKET_SIZE)
                    ack = TCP_packet.unpack_segment(raw_ack)
                except socket.timeout:
                    continue

                if ack.is_ack() and ack.ack_num == msg.seq_num + 1:
                    self.seq_num += len(chunk)
                    break

        fin = TCP_packet(self.seq_num, self.seq_num, 0, 0, 1, b'')
        raw_fin = fin.pack_segment()
        self.sendto(raw_fin)
        while True:
            try:
                self.udp_socket.settimeout(ACK_TIMEOUT)
                raw_ack = self.recvfrom(TCP_packet.PACKET_SIZE)
                ack = TCP_packet.unpack_segment(raw_ack)
                if ack.ack_num == fin.seq_num + 1 and fin.is_fin():
                    break
                if ack.is_syn():
                    break
            except socket.timeout:
                self.sendto(raw_fin)

        # print(id + " END SENDING")
        return len(data)

    def recv(self, n: int, id: str):
        # print(id + " START RECEIVING")
        self.seq_num += 100

        while True:
            self.udp_socket.settimeout(None)
            raw_syn = self.recvfrom(TCP_packet.PACKET_SIZE)
            syn = TCP_packet.unpack_segment(raw_syn)
            if syn.is_syn():
                exp_seq_num = syn.seq_num + 1
                synack = TCP_packet(self.seq_num, syn.seq_num + 1, 1, 1, 0, b'')
                raw_synack = synack.pack_segment()
                self.sendto(raw_synack)
                break

        while True:
            raw_msg = self.recvfrom(TCP_packet.PACKET_SIZE)
            msg = TCP_packet.unpack_segment(raw_msg)
            if msg.is_syn():
                self.sendto(raw_synack)
            else:
                break

        chunks = {}
        while True:
            packet_valid = True

            if msg.is_ack():
                packet_valid = False
            elif msg.seq_num != exp_seq_num:
                packet_valid = False
                if chunks.get(msg.seq_num) == msg.data:
                    ack = TCP_packet(self.seq_num, msg.seq_num + 1, 1, 0, 0, msg.data)
                    raw_ack = ack.pack_segment()
                    self.sendto(raw_ack)

            if packet_valid:
                if msg.is_fin():
                    break
                exp_seq_num += len(msg.data)
                chunks[msg.seq_num] = msg.data

                ack = TCP_packet(self.seq_num, msg.seq_num + 1, 1, 0, 0, msg.data)
                raw_ack = ack.pack_segment()
                self.sendto(raw_ack)

            self.udp_socket.settimeout(None)
            raw_msg = self.recvfrom(TCP_packet.PACKET_SIZE)
            msg = TCP_packet.unpack_segment(raw_msg)

        ack = TCP_packet(self.seq_num, msg.seq_num + 1, 1, 0, 1, msg.data)
        raw_ack = ack.pack_segment()
        self.sendto(raw_ack)

        while True:
            try:
                self.udp_socket.settimeout(FIN_TIMEOUT)
                raw_fin = self.recvfrom(TCP_packet.PACKET_SIZE)
                fin = TCP_packet.unpack_segment(raw_fin)
                if fin.is_fin():
                    self.sendto(raw_ack)
                else:
                    break
            except socket.timeout:
                break

        # print(id + " END RECEIVING")
        data = b''.join(list(map(lambda x: x[1], sorted(chunks.items()))))
        return data[:n]
