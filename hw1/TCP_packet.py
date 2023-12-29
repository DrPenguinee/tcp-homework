import struct


class TCP_packet:
    HEADER_SIZE = 15
    MSS = 50
    # maximum segment size; the max of the data HEADER_FORMAT explanation:
    # seq_num == 4 bytes, ack_num == 4 bytes,
    # header_len == 2 bytes, data_size == 2 bytes,
    # ACK == 1 byte, SYN == 1 byte, FIN == 1 byte,
    HEADER_FORMAT = '2I2H3b' + str(MSS) + 's'
    PACKET_SIZE = HEADER_SIZE + MSS

    def __init__(self, seq_num: int, ack_num: int, ACK: int, SYN: int, FIN: int, data: bytes):
        self.seq_num = seq_num
        self.ack_num = ack_num
        self.ACK = ACK
        self.SYN = SYN
        self.FIN = FIN
        self.data = data

    def is_syn(self) -> bool:
        return self.ACK == 0 and self.SYN == 1 and self.FIN == 0

    def is_synack(self) -> bool:
        return self.ACK == 1 and self.SYN == 1 and self.FIN == 0

    def is_ack(self) -> bool:
        return self.ACK == 1 and self.SYN == 0 and self.FIN == 0

    def is_fin(self) -> bool:
        return self.ACK == 0 and self.SYN == 0 and self.FIN == 1

    def is_finack(self) -> bool:
        return self.ACK == 1 and self.SYN == 0 and self.FIN == 1

    def pack_segment(self) -> bytes:
        data_size = len(self.data)
        empty_size = self.MSS - data_size
        data = self.data + b' ' * empty_size

        return struct.pack(self.HEADER_FORMAT,
                           self.seq_num, self.ack_num,
                           self.HEADER_SIZE, data_size,
                           self.ACK, self.SYN, self.FIN,
                           data)

    @classmethod
    def unpack_segment(cls, packed_segment):
        (seq_num, ack_num, header_size, data_size, ACK, SYN, FIN, data) = struct.unpack(TCP_packet.HEADER_FORMAT, packed_segment)
        data = data[:data_size]
        x = cls(seq_num, ack_num, ACK, SYN, FIN, data)
        return x
