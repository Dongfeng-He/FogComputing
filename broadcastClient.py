

from __future__ import print_function

from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor


class BroadcastClientProtocol(DatagramProtocol):

    def __init__(self, socket):
        self.socket = socket

    def startProtocol(self):
        port = 9999
        self.transport.setBroadcastAllowed(True)
        message = b"fff"
        self.transport.write(message, ("<broadcast>", port))

    def datagramReceived(self, data, addr):
        print(data)
        self.socket.append(addr)


# 0 means any port, we don't care in this case
reactor.listenUDP(0, BroadcastClient())
reactor.run()