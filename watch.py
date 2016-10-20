import collections
import math
import socket


DEF_MACADDR = ['2KTR', '2KZ8', '2KZ9', '2MJS', '2KTM']


# This class read data from watches via UDP.
class watchData(object):
    def __init__(self, ip_local, port_from_watch, port_to_watch, ip_reg, port_from_reg, port_to_reg, watch_num):
        self.ip_local = ip_local
        self.port_from_watch = port_from_watch
        self.port_to_watch = port_to_watch
        self.ip_reg = ip_reg
        self.port_from_reg = port_from_reg
        self.port_to_reg = port_to_reg
        self.watch_num = watch_num

        # socket between watch and presentation machine
        self.sock_watch = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock_watch.bind((self.ip_local, self.port_from_watch))

        # socket between presentation machine and registration machine.
        self.sock_reg = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.count = 0

        # Data queue to store all the gyro magnitude data from 5 watches.
        self.data_queue = [collections.deque(maxlen=100) for x in range(self.watch_num)]
        self.watch_ip_address = {}  # dictionary to store all watch ip address
        self.registration_data = {}  # dictionary to store all registration status

    # convert the 2 bytes data to a integer
    def trans(self, a, b):
        c = a * (2 ** 8)
        c = c + b
        if c > 2 ** 15:
            c = (2 ** 16 - c) * -1
        return c

    # convert the 8 bytes timestamp to float
    def bytes2float(self, byte_array):
        value = (byte_array[0] & 0xff) | ((byte_array[1] << 8) & 0xff00) | ((byte_array[2] << 16) & 0xff0000) \
                | ((byte_array[3] << 24) & 0xff000000)
        value += ((((byte_array[4]) & 0xff) | ((byte_array[5] << 8) & 0xff00)) / 1000.0)
        return value

    # receive data from watch, parse the data send all watch data to registration server.
    def read_from_watch(self):
        while True:
            data, addr = self.sock_watch.recvfrom(1024)
            data = bytearray(data)
            if data[4:5].decode("ascii") == 'w':  # unpack the watch IMU and battery status data package
                device_id = data[0:4].decode("ascii")
                data_type = data[4:5].decode("ascii")
                if (len(self.watch_ip_address) < 5) and (device_id in self.watch_ip_address.keys()) < 5:
                    self.watch_ip_address[device_id] = addr[0]
                gyro = [0 for x in range(3)]
                num = (len(data) - 5) / 12
                for i in range(self.watch_num):
                    if device_id == DEF_MACADDR[i]:
                        for j in range(num):
                            gyro[0] = (self.trans(data[5 + j * 12 + 7], data[5 + j * 12 + 6]) / 10000.0)*57.3
                            gyro[1] = (self.trans(data[5 + j * 12 + 9], data[5 + j * 12 + 8]) / 10000.0)*57.3
                            gyro[2] = (self.trans(data[5 + j * 12 + 11], data[5 + j * 12 + 10]) / 10000.0)*57.3

                            gyro_mag = math.sqrt(gyro[0] * gyro[0] + gyro[1] * gyro[1] + gyro[2] * gyro[2])
                            send_package = device_id + " " + data_type + " " + str(gyro_mag)
                            self.data_queue[i].append(gyro_mag)
                            self.sock_reg.sendto(send_package, (self.ip_reg, self.port_to_reg))

            if data[4:5].decode("ascii") == 'b':  # unpack the watch battery package
                device_id = data[0:4].decode("ascii")
                data_type = data[4:5].decode("ascii")
                battery_remain = data[5]
                send_package = device_id + " " + data_type + " " + str(battery_remain)
                self.sock_reg.sendto(send_package, (self.ip_reg, self.port_to_reg))


    def get_gyro_data(self):
        return self.data_queue

    def send_to_watch(self, message, device_id):
        self.sock_watch.sendto(message, (self.watch_ip_address[device_id], self.port_to_watch))

    def read_from_registration(self):
        while True:
            recv_data, addr = self.sock_reg.recvfrom(1024)
            self.registration_data = eval(recv_data)

    def get_registration_data(self):
        return self.registration_data