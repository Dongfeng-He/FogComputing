import socket
import json
import threading
import time

class Client:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    fog_task_id = 1
    cloud_task_id = 10000
    task_message = {'message_type': 'task', 'task_id': None, 'task_type': None, 'task_name': None, 'content': None, \
                    'cloud_processing': False, 'offload_times': 0, 'offloading_fog': [], 'max_offload': 4,
                    'time_requirement': 10000, \
                    'estimated_queuing_time': 0, 'queuing_time': 0, 'estimated_execution_time': 0, 'execution_time': 0}
    original_task_message = task_message
    original_task_message['task_id'] = 1
    original_task_message['task_type'] = 'medium'
    original_task_message['task_name'] = "medium"
    original_task_message['time_requirement'] = 0.05
    original_task_message['content'] = 1
    fog_message = original_task_message.copy()
    fog_message['cloud_processing'] = False
    cloud_message = original_task_message.copy()
    cloud_message['cloud_processing'] = True

    def sendMessage(self):
        while True:
            task_message = self.fog_message
            task_message['task_id'] = self.fog_task_id
            self.fog_task_id += 1
            sending_message = bytes(json.dumps(task_message), "ascii")
            self.sock.send(sending_message)

            task_message = self.cloud_message
            task_message['task_id'] = self.cloud_task_id
            self.fog_task_id += 1
            sending_message = bytes(json.dumps(task_message), "ascii")
            self.sock.send(sending_message)
            time.sleep(1)


    def __init__(self, address, port):
        self.sock.connect((address, port))
        iThread = threading.Thread(target = self.sendMessage)
        iThread.daemon = True
        iThread.start()
        while True:
            data = self.sock.recv(1024)
            if not data:
                break;
            else:
                print(data)


if __name__=="__main__":
    client = Client('172.20.10.2', 10000)