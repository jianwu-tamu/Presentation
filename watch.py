import collections
import math
import socket


DEF_MACADDR = ['2VR7', '2KMX', '9049', '9063']

# This class read data from watches via UDP.
class watchData(object):
    def __init__(self, ip, port, watch_num):
        self.ip = ip
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.watch_num = watch_num
        self.data_queue = [collections.deque(maxlen=100) for x in range(self.watch_num)]

    def sock_bind(self):
        self.sock.bind((self.ip, self.port))

    def read(self):
        while True:
            data, addr = self.sock.recvfrom(1024)
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