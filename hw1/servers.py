import os
import random
import string
import time

from protocol import MyTCPProtocol


class Base:
    def __init__(self, socket: MyTCPProtocol, iterations: int, msg_size: int):
        self.socket = socket
        self.iterations = iterations
        self.msg_size = msg_size


class EchoServer(Base):

    def run(self):
        # start_time = time.time()
        for i in range(self.iterations):
            # print("--- %s seconds ---" % (time.time() - start_time))
            if i % 1000 == 0:
                print("RUN NEW SERVER ITERATION: " + str(i))
            # print("SERVER receiving")
            msg = self.socket.recv(self.msg_size, "server " + str(i))
            # print("SERVER sending")
            self.socket.send(msg, "server " + str(i))
            
class EchoClient(Base):

    def run(self):
        # start_time = time.time()
        for i in range(self.iterations):
            # print("--- %s seconds ---" % (time.time() - start_time))
            # print("RUN NEW CLIENT ITERATION: " + str(i))
            msg = os.urandom(self.msg_size)

            # print("CLIENT sending")
            n = self.socket.send(msg, "client " + str(i))
            assert n == self.msg_size
            # print("CLIENT receiving")
            assert msg == self.socket.recv(n, "client " + str(i))
