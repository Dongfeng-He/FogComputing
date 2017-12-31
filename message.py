class TaskMessage:
    def __init__(self, task_type, task_name, content,\
                 cloud_processing = False, offload_times = 0, time_requirement = 100000):
        self.task_type = task_type
        self.task_name = task_name
        self.content = content
        self.cloud_processing = cloud_processing
        self.offload_times = offload_times
        self.time_requirement = time_requirement


task_message = {'message_type':'task', 'task_type': None, 'task_name': None, 'content': None, \
                'cloud_processing': False, 'offload_times': 0, 'max_offload': 4, 'time_requirement': 10000}

state_message = {'message_type':'state', 'task_time':None}

fog_hello_message = {'message_type':'fog_hello', 'tcp_port':None}

fog_ready_message = {'message_type':'fog_ready'}

class FogDiscoveryMessage:
    # when a new end node joins a network, broadcast the a discovery message,
    # only fogs respond to this message, end node can calculate the link delay and fog sockets
    pass

class FogRegMessage:
    # when a new fog joins a network, register with the management node of the network
    # how to find the management node?
    pass

class FogHello:
    # when a new fog joins a network, broadcast to other fogs
    # how to discover the other fogs?
    pass

class FogUpdateMessage:
    # share queuing time
    pass

class AlarmMessage:
    pass

class FogTestMessage:
    # management node periodically send test message to fogs, fogs respond to verify their availability
    pass