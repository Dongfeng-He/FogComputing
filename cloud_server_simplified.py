from twisted.internet import reactor, protocol, task
import json
import redis
from tasks import light, medium, heavy, resetTaskTime, resetQueueState, getAllTaskTime, taskInQueue
import time
from functions import unpack


# Cloud server is a simplified fog server. Only preserve the task processing function
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

        if task_message["task_name"] == "light":
            light_task_num = self.factory.r.get('light_task_num')
            if light_task_num == None:
                self.factory.r.set('light_task_num', 1)
            else:
                self.factory.r.set('light_task_num', int(light_task_num) + 1)
            enqueue_time = time.time()
            d = light.delay(task_message, enqueue_time)
            d.addCallback(respond)
            d.addErrback(onError)
        elif task_message["task_name"] == "medium":
            medium_task_num = self.factory.r.get('medium_task_num')
            if medium_task_num == None:
                self.factory.r.set('medium_task_num', 1)
            else:
                self.factory.r.set('medium_task_num', int(medium_task_num) + 1)
            enqueue_time = time.time()
            d = medium.delay(task_message, enqueue_time)
            d.addCallback(respond)
            d.addErrback(onError)
        elif task_message["task_name"] == "heavy":
            heavy_task_num = self.factory.r.get('heavy_task_num')
            if heavy_task_num == None:
                self.factory.r.set('heavy_task_num', 1)
            else:
                self.factory.r.set('heavy_task_num', int(heavy_task_num) + 1)
            enqueue_time = time.time()
            d = heavy.delay(task_message, enqueue_time)
            d.addCallback(respond)
            d.addErrback(onError)


class FogServerFactory(protocol.ClientFactory):
    protocol = FogServerProtocol
    print("Cloud server is running.")

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
