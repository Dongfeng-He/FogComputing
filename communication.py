import socket

class UDPBroadcaster:
    def __init__(self, des_port = 21570, my_port = 21571, buffsize = 1024):
        self.des_host = '<broadcast>'
        self.des_port = des_port
        self.my_port = my_port
        self.buffsize = buffsize
        self.des_address = (self.des_host, self.des_port)
        self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.s.bind(("", self.my_port))
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    def send(self, data):
        self.s.sendto(bytes(data,"ascii"), self.des_address)
        self.s.close()


class UDPListener:
    def __init__(self, my_port, buffsize = 1024):
        self.my_port = my_port
        self.buffsize = buffsize
        self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.s.bind(("", self.my_port))

    def listen(self):
        data, address = self.s.recvfrom(self.buffsize)
        self.s.close()
        return data, address



