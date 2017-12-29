from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor


class MulticastPingPong(DatagramProtocol):

    def startProtocol(self):
        """
        Called after protocol has started listening.
        """
        # Set the TTL>1 so multicast will cross router hops:设置TTL>1，以便跳过路由器，TTL定义最多跳几次
        self.transport.setTTL(5)
        # Join a specific multicast group:加入到一个具体的组播组
        self.transport.joinGroup("228.0.0.5")

    def datagramReceived(self, datagram, address):
        print("Datagram %s received from %s" % (repr(datagram), repr(address)))
        if datagram == "Client: Ping":
            # Rather than replying to the group multicast address, we send the
            # reply directly (unicast) to the originating port:
            self.transport.write(b"Server: Pong", address)


# We use listenMultiple=True so that we can run MulticastServer.py and
# MulticastClient.py on same machine: 使listenMultiple=True才能在同一台机器上运行客户端和服务器。
reactor.listenMulticast(8005, MulticastPingPong(), listenMultiple=True)
reactor.run()