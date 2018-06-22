# ---------- This file is used to specify message format ----------

# Used by client and fog node to send tasks
task_message = {'message_type':'task', 'task_id':0, 'task_type': None, 'task_name': None, 'content': None, \
                'cloud_processing': False, 'offload_times': 0, 'offloading_fog':[], 'max_offload': 4, 'time_requirement': 10000,\
                'estimated_queuing_time': 0, 'queuing_time': 0, 'estimated_execution_time': 0, 'execution_time': 0, 'distribution_time':0, 'sending_time':0, 'process_by': 'f'}

# Used by fog node and cloud server to return results
result_message = {'message_type':'result', 'task_id':None, 'content':None, 'time_requirement': None, 'sending_time':None, 'distribution_time':None, 'execution_time':None, 'task_type':None, 'offload_times':None, 'process_by': 'f'}

# Used by fog node to share estimated waiting time with each other
state_message = {'message_type':'state', 'task_time':None}

# Used by new fog node that enters the fog computing network to initialize new fog node discovery
fog_hello_message = {'message_type':'fog_hello', 'tcp_port':None}

# Used by new endpoint that enters the fog computing network to initialize new endpoint discovery
endpoint_hello_message = {'message_type':'endpoint_hello'}

# Used by fog node to respond to fog_hello_message
fog_ready_message = {'message_type':'fog_ready', 'send_time': None}

# Used by new fog node to respond to fog_ready_message
fog_ready_ack_message = {'message_type':'fog_ready_ack', 'send_time': None}

# Used by fog node to respond to endpoint_hello_message
fog_ack_message = {'message_type':'fog_ack', 'tcp_port':None}







