import collections
import math
import socket
import struct
import thread


DEF_MACADDR = ['2VTX', '2VR7', '2ZX7', '2VN8', '2KMX']

# This class read data from watches via UDP.
class watchData(object):
    def __init__(self, ip, port, ip1, port1, watch_num):
        self.ip = ip
        self.port = port
        self.ip1 = ip1
        self.port1 = port1
        self.watch_num = watch_num
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        self.data_queue = [collections.deque(maxlen=100) for x in range(self.watch_num)]
        self.sock.bind((self.ip, self.port))

    def read(self):
        while True:
            data, addr = self.sock.recvfrom(1024)
            self.sock2.sendto(data, (self.ip1, self.port1))
            parsed_data = data.split(' ')
            if (parsed_data[2] == '3'):
                gyro_x = float(parsed_data[3])
                gyro_y = float(parsed_data[4])
                gyro_z = float(parsed_data[5])
                gyro_mag = math.sqrt(gyro_x*gyro_x + gyro_y*gyro_y + gyro_z*gyro_z) * 57.3
                for i in range(self.watch_num):
                    if (parsed_data[0] == DEF_MACADDR[i]):
                        self.data_queue[i].append(gyro_mag)

    def get_data(self):
        return self.data_queue