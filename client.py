from twisted.internet import reactor, protocol
from functions import csvReader
from message import task_message, endpoint_hello_message
import json


class ClientProtocol(protocol.Protocol):
    task_id = 0

    def connectionMade(self):
        self._peer = self.transport.getPeer()
        print("Connected to fog server:", self._peer)

    def dataReceived(self, data):
        data = data.decode("ascii")
        message = json.loads(data)

        self.task_id += 1
        original_task_message = task_message
        original_task_message['task_id'] = self.task_id
        original_task_message['task_type'] = 'light'
        original_task_message['task_name'] = "add"
        original_task_message['time_requirement'] = 0.05
        original_task_message['content'] = 1
        # cloud processing
        original_task_message['cloud_processing'] = False
        sending_message = bytes(json.dumps(original_task_message), "ascii")

        if message["message_type"] == "fog_ready":
            self.transport.write(sending_message)
        elif message["message_type"] == "result":
            print("Result is: ", message["content"])
            self.transport.write(sending_message)

    def connectionLost(self, reason):
        print("Disconnected from", self.transport.getPeer())


class ClientFactory(protocol.ClientFactory):
    protocol = ClientProtocol

    def __init__(self):
        pass


    def clientConnectionFailed(self, connector, reason):
        print("Connection failed")
        reactor.stop()

    def clientConnectionLost(self, connector, reason):
        print("Connection lost")
        reactor.stop()


class MulticastClientProtocol(protocol.DatagramProtocol):
    def __init__(self, group, multicast_port, client_num):
        self.group = group
        self.multicast_port = multicast_port
        self.client_num = client_num
        self.connected = False

    def startProtocol(self):
        endpoint_hello = endpoint_hello_message
        self.transport.joinGroup(self.group)
        self.transport.write(bytes(json.dumps(endpoint_hello), "ascii"), (self.group, self.multicast_port))

    def datagramReceived(self, data, addr):
        if self.connected == False:
            data = data.decode("ascii")
            message = json.loads(data)
            if message["message_type"] == "fog_ack":
                fog_ip = addr[0]
                tcp_port = message["tcp_port"]
                for i in range(self.client_num):
                    reactor.connectTCP(fog_ip, tcp_port, ClientFactory())
                self.connected = True




def main():
    #endpoint_factory = ClientFactory()
    multicast_group = "228.0.0.5"
    multicast_port = 8005
    client_num = 1
    multicast_client_protocol = MulticastClientProtocol(multicast_group, multicast_port, client_num)
    reactor.listenMulticast(multicast_port, multicast_client_protocol, listenMultiple=True)
    reactor.run()

if __name__ == "__main__":
    main()





