"""
An example client. Run simpleserv.py first before running this.
"""
from __future__ import print_function

from twisted.internet import reactor, protocol
from twisted.protocols.basic import LineReceiver

# a client protocol

class EchoClient(LineReceiver):
    """Once connected, send a message, then print the result."""

    def connectionMade(self):
        self.sendLine(b"hello, world!")

    def dataReceived(self, data):
        "As soon as any data is received, write it back."
        print("Server said:", data)
        #self.sendLine(bytes(input(), "ascii"))


    def connectionLost(self, reason):
        print("connection lost")


class EchoFactory(protocol.ClientFactory):
    protocol = EchoClient

    def clientConnectionFailed(self, connector, reason):
        print("Connection failed - goodbye!")
        reactor.stop()

    def clientConnectionLost(self, connector, reason):
        print("Connection lost - goodbye!")
        reactor.stop()

class BroadcastClient(protocol.DatagramProtocol):
    def startProtocol(self):
        host = "<broadcast>"
        port = 9999
        self.transport.setBroadcastAllowed(True)
        self.transport.write(b"asdf", ("<broadcast>", port))
        print("now we broadcast at port %d" % port)


    def datagramReceived(self, data, addr):
        print("received %r from %s" % (data, addr))


# this connects the protocol to a server running on port 8000
def main():
    f = EchoFactory()
    reactor.connectTCP("localhost", 8000, f)
    reactor.listenUDP(0, BroadcastClient())
    reactor.run()


# this only runs if the module was *not* imported
if __name__ == '__main__':
    main()