from twisted.internet import reactor, protocol, task
import json
import redis
from tasks import light, medium, heavy, resetTaskTime, resetQueueState, getAllTaskTime, taskInQueue, getWaitingTime, getExecutionTime
from message import state_message, fog_hello_message, fog_ready_message, fog_ack_message, fog_ready_ack_message
from communication import find_idle_port
import socket
import time
from functions import unpack
import sys


class FogServerProtocol(protocol.Protocol):
    # When a connection is made, this function will be triggered, if a new fog node or endpoint
    # is connected to this fog node, this fog node will send a fog_ready_message
    def connectionMade(self):
        self._peer = self.transport.getPeer()
        if self._peer.host == self.factory.cloud_ip:
            self.factory.cloud_connection = self
            print("Connected to %s (cloud)" % self._peer.host)
        else:
            fog_ready = fog_ready_message
            fog_ready['send_time'] = time.time()
            fog_ready = bytes(json.dumps(fog_ready), "ascii")
            self.transport.write(fog_ready)

    # When this fog node receives data, this function will be triggered
    def dataReceived(self, data):
        data = data.decode("ascii")
        unpacked_data = unpack(data)
        for data in unpacked_data:
            message = json.loads(data)
            if message["message_type"] == "task":
                # Save this connection to factory
                self.factory.current_connection = self
                # Distribute this task to local processing, neighbour fog node or cloud server
                self.taskDistributor(message)
                print("Receive a task from %s (task ID: %d)" % (self.transport.getPeer().host, message['task_id']), end = ' ')
                print("Offloading fogs: ", message['offloading_fog'])
            elif message["message_type"] == "result":
                # Handle the received results
                self.resultHandler(message)
                print("Receive a task result from %s (task ID: %d)" % (self.transport.getPeer().host, message['task_id']))
                # Handle the received state information of neighbour fog nodes
            elif message["message_type"] == "state":
                self.stateHandler(message)
                # Handle the fog_ready_message, respond a fog_ready_ack_message
            elif message["message_type"] == "fog_ready":
                self.saveFogNeighbourConnection()
                fog_ready_ack = fog_ready_ack_message
                fog_ready_ack['send_time'] = message['send_time']
                self.transport.write(bytes(json.dumps(fog_ready_ack), "ascii"))
                # Handle the fog_ready_ack_message, calculate delay
            elif message["message_type"] == "fog_ready_ack":
                self.factory.delay_table[self] = time.time() - message['send_time']
                print("Connected to %s (fog)" % self.transport.getPeer().host)

    # When a connection is lost, this function will be triggered
    def connectionLost(self, reason):
        print("Disconnected from", self.transport.getPeer().host)
        self.deleteFogNeighbourConnection()

    # Analysis the incoming task, status of the task queue and neighbour fog state table to determine
    # where to process the task
    def taskInspection(self, task_message):
        estimated_waiting_time = getWaitingTime()
        task_message['estimated_queuing_time'] = estimated_waiting_time
        task_message['estimated_execution_time'] = getExecutionTime(task_message['task_type'])
        fog_waiting_time = self.factory.findIdleFog(task_message["offloading_fog"])[1]
        if self.factory.cloud_mode == True and self.factory.fog_mode == True:
            if task_message["cloud_processing"] == True:
                operation = "cloud"
            else:
                if estimated_waiting_time <= task_message["time_requirement"] or \
                        (task_message["offload_times"] >= task_message["max_offload"] and task_message["task_type"] != "heavy") or \
                        (estimated_waiting_time <= fog_waiting_time and task_message["task_type"] != "heavy"):
                    operation = "accept"
                elif (task_message["offload_times"] >= task_message["max_offload"] and task_message["task_type"] == "heavy") or \
                        (estimated_waiting_time <= fog_waiting_time and task_message["task_type"] == "heavy"):
                    operation = "cloud"
                else:
                    operation = "fog"
        elif self.factory.cloud_mode == False and self.factory.fog_mode == True:
            if estimated_waiting_time <= task_message["time_requirement"] or \
                    task_message["offload_times"] >= task_message["max_offload"] or \
                    estimated_waiting_time <= fog_waiting_time:
                operation = "accept"
            else:
                operation = "fog"
        elif self.factory.cloud_mode == True and self.factory.fog_mode == False:
            if task_message["cloud_processing"] == True or \
                    (estimated_waiting_time >= task_message["time_requirement"] and task_message['task_type'] == "heavy"):
                operation = "cloud"
            else:
                operation = "accept"
        elif self.factory.cloud_mode == False and self.factory.fog_mode == False:
            operation = "accept"
        print("Current waiting time: %f" % (estimated_waiting_time))
        print("Fog waiting time: %f" % (fog_waiting_time))
        print("Chosen operation: %s" % (operation))
        return operation

    # Send the task to the best neighbour fog node
    def taskOffloading(self, task_message):
        task_id = task_message["task_id"]
        self.factory.send_back_table[task_id] = self
        fog = self.factory.findIdleFog(task_message["offloading_fog"])[0]
        task_message["offload_times"] += 1
        host = self.transport.getHost().host
        task_message["offloading_fog"].append(host)
        fog.transport.write(bytes(json.dumps(task_message), "ascii"))
        print("Offload (task ID: %d) to %s" % (task_id, fog.transport.getPeer().host))

    # Send the task to Cloud
    def taskSendToCloud(self, task_message):
        task_id = task_message["task_id"]
        self.factory.send_back_table[task_id] = self
        cloud = self.factory.cloud_connection
        cloud.transport.write(bytes(json.dumps(task_message), "ascii"))

    # Process the task locally
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
            # Use task_name.delay() to insert the task to the task queue for processing
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

    # Distribute the task to local processing, neighbour fog node or Cloud based on the
    # result of taskInspection function
    def taskDistributor(self, task_message):
        if task_message["offload_times"] == 0:
            self.factory.next_task_id += 1
        operation = self.taskInspection(task_message)
        task_message["distribution_time"] = time.time()
        if operation == "cloud":
            task_message['process_by'] = "cloud"
            self.taskSendToCloud(task_message)
        elif operation == "fog":
            task_message['process_by'] = "fog"
            self.taskOffloading(task_message)
        elif operation == "accept":
            if int(task_message['offload_times']) == 0:
                task_message['process_by'] = "local"
            self.taskProcessing(task_message)

    # Return the result to the fog node that offloads the task to this fog
    def resultHandler(self, result_message):
        task_id = result_message["task_id"]
        connection = self.factory.send_back_table[task_id]
        connection.transport.write(bytes(json.dumps(result_message), "ascii"))

    # Store the received state information of neighbour fog node in state_table in factory
    def stateHandler(self, state_message):
        self.factory.state_table[self] = state_message["task_time"]

    # Save the connection with a fog node to fog_neighbour_connection in factory
    def saveFogNeighbourConnection(self):
        self.factory.fog_neighbour_connection.append(self)

    # Delete the connection with a fog node from fog_neighbour_connection in factory
    def deleteFogNeighbourConnection(self):
        if self in self.factory.fog_neighbour_connection:
            self.factory.fog_neighbour_connection.remove(self)


# This is the factory that applies FogServerProtocol and performs state sharing & best fog node selection
class FogServerFactory(protocol.ClientFactory):
    protocol = FogServerProtocol

    def __init__(self, r, task_id_root, cloud_ip, fog_mode = True, cloud_mode = True, sharing_interval = 1):
        self.fog_neighbour_connection = []
        self.cloud_ip = cloud_ip
        self.cloud_connection = None
        self.current_connection = None
        self.delay_table = {}
        self.state_table = {}
        self.state_table_without_offloading_fog = {}
        self.send_back_table = {}
        self.previous_task_time = 0
        self.r = r
        self.next_task_id = task_id_root
        self.fog_mode = fog_mode
        self.cloud_mode = cloud_mode
        # Specify the period of state sharing
        self.sharing_interval = sharing_interval
        # Start state sharing
        self.lc = task.LoopingCall(self.shareState)
        self.lc.start(self.sharing_interval)

    # Send the state information to neighbour fog nodes
    def shareState(self):
        waiting_time = getWaitingTime()
        state_sharing_message = state_message
        state_sharing_message["task_time"] = waiting_time
        state_sharing_message = bytes(json.dumps(state_sharing_message), "ascii")
        if self.fog_neighbour_connection:
            for fog in self.fog_neighbour_connection:
                fog.transport.write(state_sharing_message)

    # Find the best neighbour fog node with minimal estimated waiting time
    def findIdleFog(self, offloaded_fog_ip):
        self.state_table_without_offloading_fog = self.state_table.copy()
        if len(self.state_table):
            if len(offloaded_fog_ip) != 0:
                for fog_connection in self.state_table.keys():
                    fog_connection_ip = fog_connection.transport.getPeer().host
                    if fog_connection_ip in offloaded_fog_ip:
                        del self.state_table_without_offloading_fog[fog_connection]
            if len(self.state_table_without_offloading_fog) == 0:
                fog_connection, task_time = None, 1000000
            else:
                for fog_connection in self.state_table_without_offloading_fog.keys():
                    total_fog_time = self.state_table_without_offloading_fog[fog_connection] + self.delay_table[fog_connection]
                    self.state_table_without_offloading_fog[fog_connection] = total_fog_time
                fog_connection, all_task_time = min(self.state_table_without_offloading_fog.items(), key=lambda x: x[1])
                fog_ip = fog_connection.transport.getPeer().host
                task_time = all_task_time
        else:
            fog_connection, task_time = None, 1000000
        return fog_connection, task_time


# This class is used to perform new fog and new endpoint discovery
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
        self.ip = self.get_host_ip()
        print("Fog server running at %s:%s" % (self.ip, self.tcp_port))

    def startProtocol(self):
        self.transport.setTTL(5) # Set the TTL>1 so multicast will cross router hops
        self.transport.joinGroup(self.group)
        # When a fog node is launched, it will multicast a fog_hello_message to initialize fog discovery
        self.transport.write(bytes(json.dumps(self.fog_hello), "ascii"), (self.group, self.multicast_port))

    def datagramReceived(self, data, addr):
        data = data.decode("ascii")
        message = json.loads(data)
        # The fog node that receives a fog_hello_message form a connection with the new fog node
        if message["message_type"] == "fog_hello":
            fog_ip = addr[0]
            tcp_port = message["tcp_port"]
            if tcp_port != self.tcp_port or fog_ip != self.ip:
                reactor.connectTCP(fog_ip, tcp_port, self.fog_factory)
        # The fog node that receives a endpoint_hello_message respond a fog_ack_message
        elif message["message_type"] == "endpoint_hello":
            self.transport.write(bytes(json.dumps(self.fog_ack), "ascii"), (self.group, self.multicast_port))

    # Get the IP of myself
    def get_host_ip(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(('8.8.8.8', 80))
            ip = s.getsockname()[0]
        finally:
            s.close()
        return ip


def main():
    # Connect to Redis
    r = redis.Redis(host='localhost', port=6379, decode_responses=True)
    resetTaskTime()
    resetQueueState()
    # You need to modify the cloud_ip to the IP of your own Cloud instance
    cloud_ip = '54.206.45.203'
    cloud_port = 10000
    # Find an available port
    tcp_port = find_idle_port()
    # The multicast group for multicasting discovery message
    multicast_group = "228.0.0.5"
    multicast_port = 8005
    task_id_root = 10000
    # Create the fog factory
    fog_factory = FogServerFactory(r, task_id_root, cloud_ip)
    # Create the multicast protocol
    multicast_server_protocol = MulticastSeverProtocol(tcp_port, fog_factory, multicast_group, multicast_port)
    # Connect to cloud server
    reactor.connectTCP(cloud_ip, cloud_port, fog_factory)
    # Start fog server and listen to tcp_port
    reactor.listenTCP(tcp_port, fog_factory)
    # Start multicast server and listen to multicast_port
    reactor.listenMulticast(multicast_port, multicast_server_protocol, listenMultiple=True)
    reactor.run()


if __name__ == "__main__":
    main()












