from twisted.internet import reactor, protocol
from functions import csvReader
from message import task_message
import json



class ClientProtocol(protocol.Protocol):
    def connectionMade(self):
        self._peer = self.transport.getPeer()
        print("Connected to fog server:", self._peer)

    def dataReceived(self, data):
        data = data.decode("ascii")
        message = json.loads(data)
        if message["message_type"] == "fog_ready":
            self.transport.write(self.factory.task_message)
        elif message["message_type"] == "result":
            print("Result is: ", message["content"])
            self.transport.write(self.factory.task_message)

    def connectionLost(self, reason):
        print("Disconnected from", self.transport.getPeer())


class ClientFactory(protocol.ClientFactory):
    protocol = ClientProtocol

    def __init__(self):
        original_task_message = task_message
        original_task_message['task_type'] = 'light'
        original_task_message['task_name'] = "add"
        original_task_message['content'] = csvReader("wind.csv")
        self.task_message = bytes(json.dumps(original_task_message), "ascii")


    def clientConnectionFailed(self, connector, reason):
        print("Connection failed")
        reactor.stop()

    def clientConnectionLost(self, connector, reason):
        print("Connection lost")
        reactor.stop()



def fogDiscovery():
    des_port = 10000
    my_port = 33235
    broadcaster = UDPBroadcaster(des_port=des_port, my_port=my_port)
    broadcaster.send("FogDiscovery")
    listener = UDPListener(my_port=my_port)  # listener can only be created after broadcaster releases the port
    data, address = listener.listen()
    listener.close()
    host = address[0]
    port = int(data.decode("ascii"))
    return host, port



def main():
    host, port = fogDiscovery()
    for i in range(10):
        reactor.connectTCP(host, port, ClientFactory())
    reactor.run()

if __name__ == "__main__":
    main()





