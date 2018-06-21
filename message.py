class TaskMessage:
    def __init__(self, task_type, task_name, content,\
                 cloud_processing = False, offload_times = 0, time_requirement = 100000):
        self.task_type = task_type
        self.task_name = task_name
        self.content = content
        self.cloud_processing = cloud_processing
        self.offload_times = offload_times
        self.time_requirement = time_requirement


task_message = {'message_type':'task', 'task_id':0, 'task_type': None, 'task_name': None, 'content': None, \
                'cloud_processing': False, 'offload_times': 0, 'offloading_fog':[], 'max_offload': 4, 'time_requirement': 10000,\
                'estimated_queuing_time': 0, 'queuing_time': 0, 'estimated_execution_time': 0, 'execution_time': 0, 'distribution_time':0, 'sending_time':0, 'process_by': 'f'}

result_message = {'message_type':'result', 'task_id':None, 'content':None, 'time_requirement': None, 'sending_time':None, 'distribution_time':None, 'execution_time':None, 'task_type':None, 'offload_times':None, 'process_by': 'f'}

state_message = {'message_type':'state', 'task_time':None}

fog_hello_message = {'message_type':'fog_hello', 'tcp_port':None}

endpoint_hello_message = {'message_type':'endpoint_hello'}

fog_ack_message = {'message_type':'fog_ack', 'tcp_port':None}

fog_ready_message = {'message_type':'fog_ready', 'send_time': None}

fog_ready_ack_message = {'message_type':'fog_ready_ack', 'send_time': None}

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








