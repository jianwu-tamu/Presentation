import collections
import math
import socket
import struct
from watch import watchData

# This class read data from watches via UDP.
class watch3(object):
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((self.ip, self.port))
        self.data = {}

    def read(self):
        while True:
            recv_data, addr = self.sock.recvfrom(1024)
            self.data = eval(recv_data)

    def get_data(self):
        return self.data