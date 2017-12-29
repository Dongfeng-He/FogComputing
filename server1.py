from twisted.internet import reactor, protocol, defer
from twisted.protocols.basic import LineReceiver
import json
import time
from tasks import add
import redis

r = redis.Redis(host='localhost', port=6379, decode_responses=True)

class Echo(protocol.Protocol):
    """This is just about the simplest possible protocol"""

    def connectionMade(self):
        self._peer = self.transport.getPeer()
        print("Connected to", self._peer)
        self.transport.write(b"clear!")

    def _taskInspection(self, task_message):
        if task_message["cloud_processing"] == True or task_message["offload_times"] >= task_message["max_offload"]:
            operation = "cloud"
        elif task_message["time_requirement"] >= r.get('queuing_time'):
            operation = "fog"
        else:
            operation = "accept"

        return operation

    def dataReceived(self, data):
        data = data.decode("ascii")
        task_message = json.loads(data)
        operation = self._taskInspection(task_message)
        if operation == "cloud":
            pass
        elif operation == "fog":
            pass
        elif operation == "accept":
            pass

        self.transport.write(data)
        print(data)
        #self.sendLine(line)
        def error(err):
            return b'error'
        def respond(message):
            message = 'asdf' + message
            self.transport.write(bytes(json.dumps(message),"ascii"))
            print(message)
            self.transport.loseConnection()
            #self.transport.write(b'adf')
        d = add.delay(2,1)
        d.addCallback(respond)
        d.addErrback(error)






class Echo2(LineReceiver):
    """This is just about the simplest possible protocol"""



    def lineReceived(self, line):
        a = {"a": 1, "b": 2}
        b = json.dumps(a)
        print(type(b))
        "As soon as any data is received, write it back."
        self.transport.write(bytes(b, "ascii"))

class BroadcastServer(protocol.DatagramProtocol):
    def __init__(self, tcp_port):
        self.tcp_port = bytes(str(tcp_port), "ascii")

    def datagramReceived(self, data, addr):
        print("received %r from %s" % (data, addr))
        self.transport.write(self.tcp_port, addr)

def main():
    """This runs the protocol on port 8000"""

    tcp_port = 8000
    factory = protocol.ServerFactory()
    factory.protocol = Echo
    factory2 = protocol.ServerFactory()
    factory2.protocol = Echo2
    reactor.listenTCP(tcp_port, factory)
    reactor.listenTCP(8003, factory2)
    reactor.listenUDP(10000, BroadcastServer(tcp_port))
    reactor.run()


# this only runs if the module was *not* imported
if __name__ == '__main__':
    main()