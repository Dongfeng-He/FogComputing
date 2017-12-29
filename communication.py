import socket

class UDPMulticaster:
    def __init__(self, multicast_group, multicast_port, my_port, buffsize = 1024):
        self.multicast_group = multicast_group
        self.multicast_port = multicast_port
        self.my_port = my_port
        self.buffsize = buffsize
        self.des_address = (self.multicast_group, self.multicast_port)
        self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.s.bind(("", self.my_port))
        self.s.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 255)
        self.s.setblocking(0)

    def send(self, data):
        self.s.sendto(bytes(data,"ascii"), self.des_address)
        self.s.close()


class UDPListener:
    def __init__(self, my_port, buffsize = 1024, timeout = False):
        self.my_port = my_port
        self.buffsize = buffsize
        self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.s.bind(("", self.my_port))
        if timeout:
            self.s.settimeout(timeout)

    def listen(self):
        data, address = self.s.recvfrom(self.buffsize)
        data = data.decode("ascii")
        return data, address

    def close(self):
        self.s.close()


def find_idle_port():
    for port in range(10000, 65535):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(5)
            s.bind(("", port))
            s.settimeout(None)
            s.close()
            idle_port = port
            break
        except Exception:
            pass

    return idle_port
