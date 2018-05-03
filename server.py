from twisted.internet import reactor, protocol, task
import json
import redis
from tasks import add, setTaskTime, getTaskTime
from message import state_message, fog_hello_message, fog_ready_message, fog_ack_message
from communication import find_idle_port
import socket

class FogServerProtocol(protocol.Protocol):
    def connectionMade(self):
        self._peer = self.transport.getPeer()
        print("Connected to", self._peer)
        fog_ready = bytes(json.dumps(fog_ready_message), "ascii")
        self.transport.write(fog_ready)

    def taskInspection(self, task_message):
        '''
        print("task time:", self.factory.r.get(task_message["task_name"]))
        if self.factory.cloud_mode and task_message["cloud_processing"] == True or task_message["offload_times"] >= task_message["max_offload"]:
            operation = "cloud"
        elif self.factory.offloading_mode and task_message["time_requirement"] <= float(self.factory.r.get(task_message["task_name"])):
            operation = "fog"
        else:
            operation = "accept"

        if (self.factory.cloud_mode == False and \
            self.factory.offloading_mode == False) or True:pass
            '''
        estimated_task_time = float(self.factory.r.get(task_message["task_name"]))
        print(estimated_task_time)
        if self.factory.cloud_mode == True and self.factory.fog_mode == True:
            if task_message["cloud_processing"] == True:
                operation = "cloud"
            else:
                if estimated_task_time <= task_message["time_requirement"] or \
                        (task_message["offload_times"] >= task_message["max_offload"] and task_message["task_type"] != "heavy") or \
                        (estimated_task_time <= self.factory.findIdleFog(task_message["task_name"])[1] and task_message["task_type"] != "heavy"):
                    operation = "accept"
                elif (task_message["offload_times"] >= task_message["max_offload"] and task_message["task_type"] == "heavy") or \
                        (estimated_task_time <= self.factory.findIdleFog(task_message["task_name"])[1] and task_message["task_type"] == "heavy"):
                    operation = "cloud"
                else:
                    operation = "fog"
        elif self.factory.cloud_mode == False and self.factory.fog_mode == True:
            if estimated_task_time <= task_message["time_requirement"] or \
                    task_message["offload_times"] >= task_message["max_offload"] or \
                    estimated_task_time <= self.factory.findIdleFog(task_message["task_name"])[1]:
                operation = "accept"
            else:
                operation = "fog"
        elif self.factory.cloud_mode == True and self.factory.fog_mode == False:
            if task_message["cloud_processing"] == True or \
                    (estimated_task_time >= task_message["time_requirement"] and task_message['task_type'] == "heavy"):
                operation = "cloud"
            else:
                operation = "accept"
        elif self.factory.cloud_mode == False and self.factory.fog_mode == False:
            operation = "accept"

        return operation

    #TODO: 1.maintain a table of other servers; 2.periodic share task time with other fog servers
    def taskOffloading(self, task_message):
        task_id = task_message["task_id"]
        self.factory.send_back_table[task_id] = self
        fog = self.factory.findIdleFog(task_message["task_name"])[0]
        task_message["offload_times"] += 1
        host = self.transport.getHost().host
        port = self.transport.getHost().port
        task_message["offloading_fog"].append((host,port))
        fog.transport.write(bytes(json.dumps(task_message), "ascii"))
        #b = self.factory.state_table.keys()
        #for c in b:
        #    c1 = c.transport.getHost()
        #    c2 = c.transport.getPeer()
        #a = self.transport.getHost()


#


    def taskProcessing(self, task_message):
        def onError(err):
            self.transport.write("task failed, reason: ", err)

        def respond(result):
            self.transport.write(bytes(json.dumps(result), "ascii"))

        if task_message["task_name"] == "add":
            d = add.delay(task_message["content"], task_message["task_id"])
            d.addCallback(respond)
            d.addErrback(onError)

    def taskHandler(self, task_message):
        if task_message["offload_times"] == 0:
            #task_message["task_id"] = self.factory.next_task_id
            self.factory.next_task_id += 1

        operation = self.taskInspection(task_message)
        if operation == "cloud":
            pass
        elif operation == "fog":
            self.taskOffloading(task_message)
        elif operation == "accept":
            self.taskProcessing(task_message)

    def resultHandler(self, result_message):
        task_id = result_message["task_id"]
        connection = self.factory.send_back_table[task_id]
        connection.transport.write(bytes(json.dumps(result_message), "ascii"))

    def stateHandler(self, state_message):
        self.factory.state_table[self] = state_message["task_time"]
        print(self.factory.state_table)

    def saveFogNeighbourConnection(self):
        self.factory.fog_neighbour_connection.append(self)
        print(self.factory.fog_neighbour_connection)

    def deleteFogNeighbourConnection(self):
        if self in self.factory.fog_neighbour_connection:
            self.factory.fog_neighbour_connection.remove(self)
            print(self.factory.fog_neighbour_connection)


    def dataReceived(self, data):
        data = data.decode("ascii")
        message = json.loads(data)
        print(message)
        if message["message_type"] == "task":
            self.factory.current_connection = self
            self.taskHandler(message)
        elif message["message_type"] == "result":
            self.resultHandler(message)
        elif message["message_type"] == "state":
            self.stateHandler(message)
        elif message["message_type"] == "fog_ready":
            self.saveFogNeighbourConnection()


    def connectionLost(self, reason):
        print("Disconnected from", self.transport.getPeer())
        self.deleteFogNeighbourConnection()


class FogServerFactory(protocol.ClientFactory):
    protocol = FogServerProtocol

    def __init__(self, r, task_id_root, fog_mode = True, cloud_mode = True, sharing_interval = 5):
        self.fog_neighbour_connection = []
        self.current_connection = None
        self.state_table = {}
        self.send_back_table = {}
        self.r = r
        self.next_task_id = task_id_root
        self.fog_mode = fog_mode
        self.cloud_mode = cloud_mode
        self.sharing_interval = sharing_interval
        self.lc = task.LoopingCall(self.shareState)
        self.lc.start(self.sharing_interval)


    def shareState(self):
        task_time = getTaskTime()
        state_sharing_message = state_message
        state_sharing_message["task_time"] = task_time
        state_sharing_message = bytes(json.dumps(state_sharing_message), "ascii")
        if self.fog_neighbour_connection:
            for fog in self.fog_neighbour_connection:
                fog.transport.write(state_sharing_message)

    def findIdleFog(self, task_name):
        if len(self.state_table):
            fog_connection, all_task_time = min(self.state_table.items(), key=lambda x: x[1][task_name])
            task_time = all_task_time[task_name]
        else:
            fog_connection, task_time = None, 1000000
        return fog_connection, task_time



class MulticastSeverProtocol(protocol.DatagramProtocol):
    def __init__(self, tcp_port, fog_factory, group, multicast_port):
        self.group = group
        self.tcp_port = tcp_port
        self.fog_hello = fog_hello_message
        self.fog_hello['tcp_port'] = tcp_port
        self.fog_ack = fog_ack_message
        self.fog_ack['tcp_port'] = tcp_port
        self.multicast_port = multicast_port
        self.fog_factory = fog_factory
        myname = socket.getfqdn(socket.gethostname())
        self.ip = socket.gethostbyname(myname)

    def startProtocol(self):
        self.transport.setTTL(5) # Set the TTL>1 so multicast will cross router hops
        self.transport.joinGroup(self.group)
        self.transport.write(bytes(json.dumps(self.fog_hello), "ascii"), (self.group, self.multicast_port))


    def datagramReceived(self, data, addr):
        data = data.decode("ascii")
        message = json.loads(data)
        print(data)
        if message["message_type"] == "fog_hello":
            fog_ip = addr[0]
            tcp_port = message["tcp_port"]
            if tcp_port != self.tcp_port or fog_ip != self.ip:
                reactor.connectTCP(fog_ip, tcp_port, self.fog_factory)
        elif message["message_type"] == "endpoint_hello":
            self.transport.write(bytes(json.dumps(self.fog_ack), "ascii"), (self.group, self.multicast_port))




def main():
    r = redis.Redis(host='localhost', port=6379, decode_responses=True)
    setTaskTime()
    #TODO:  2. discvoery fogs 3. connect to fogs and store the connections in factory
    tcp_port = find_idle_port()
    multicast_group = "228.0.0.5"
    multicast_port = 8005
    task_id_root = 10000
    fog_factory = FogServerFactory(r, task_id_root)
    multicast_server_protocol = MulticastSeverProtocol(tcp_port, fog_factory, multicast_group, multicast_port)
    reactor.listenTCP(tcp_port, fog_factory)
    reactor.listenMulticast(multicast_port, multicast_server_protocol, listenMultiple=True)
    reactor.run()



if __name__ == "__main__":
    main()