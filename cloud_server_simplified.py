from twisted.internet import reactor, protocol, task
import json
import redis
from tasks import add, resetTaskTime, resetQueueState, getAllTaskTime, taskInQueue
import time
from functions import unpack


class FogServerProtocol(protocol.Protocol):
    def dataReceived(self, data):
        data = data.decode("ascii")
        unpacked_data = unpack(data)
        for data in unpacked_data:
            message = json.loads(data)
            print(message)
            self.taskProcessing(message)

    def connectionLost(self, reason):
        print("Disconnected from", self.transport.getPeer())

    def taskProcessing(self, task_message):
        def onError(err):
            self.transport.write("task failed, reason: ", err)

        def respond(result):
            self.transport.write(bytes(json.dumps(result), "ascii"))

        if task_message["task_name"] == "add":
            light_task_num = self.factory.r.get('light_task_num')
            if light_task_num == None:
                self.factory.r.set('light_task_num', 1)
            else:
                self.factory.r.set('light_task_num', int(light_task_num) + 1)
            enqueue_time = time.time()
            d = add.delay(task_message["content"], task_message["task_id"], enqueue_time)
            d.addCallback(respond)
            d.addErrback(onError)


class FogServerFactory(protocol.ClientFactory):
    protocol = FogServerProtocol

    def __init__(self, r):
        self.r = r


def main():
    r = redis.Redis(host='localhost', port=6379, decode_responses=True)
    resetTaskTime()
    resetQueueState()
    tcp_port = 10000
    fog_factory = FogServerFactory(r)
    reactor.listenTCP(tcp_port, fog_factory)
    reactor.run()



if __name__ == "__main__":
    main()