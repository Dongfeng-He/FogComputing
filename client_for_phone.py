import socket
import json
import threading
import time
from functions import unpack
from message import task_message
import _thread

class Client:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    fog_task_id = 1
    middle_task_id = 5000
    cloud_task_id = 10000
    task_message1 = task_message
    original_task_message = task_message1
    original_task_message['task_id'] = 1
    original_task_message['task_type'] = 'medium'
    original_task_message['task_name'] = "medium"
    original_task_message['time_requirement'] = 0.05
    original_task_message['content'] = 1
    fog_message = original_task_message.copy()
    fog_message['cloud_processing'] = False
    cloud_message = original_task_message.copy()
    cloud_message['cloud_processing'] = True
    performance = {"light_num": 0, "light_delay": 0, "light_in_time": 0, "light_avg_delay": 0, "light_in_time_rate": 0, \
                   "middle_num": 0, "middle_delay": 0, "middle_in_time": 0, "middle_avg_delay": 0,
                   "middle_in_time_rate": 0, \
                   "heavy_num": 0, "heavy_delay": 0, "heavy_in_time": 0, "heavy_avg_delay": 0, "heavy_in_time_rate": 0}

    max_offloading_time = 4

    light_task_per_min = 200
    if light_task_per_min != 0:
        light_delay = 60 / light_task_per_min
    light_time_requirement = 0.2

    middle_task_per_min = 40
    if middle_task_per_min != 0:
        middle_delay = 60 / middle_task_per_min
    middle_time_requirement = 2

    heavy_task_per_min = 0
    if heavy_task_per_min != 0:
        heavy_delay = 60 / heavy_task_per_min
    heavy_time_requirement = 5



    def sendMessage(self):
        while True:
            time.sleep(self.light_delay)
            light_message = self.task_message1.copy()
            light_message['task_id'] = 1
            light_message['task_type'] = 'light'
            light_message['task_name'] = "light"
            light_message['time_requirement'] = self.light_time_requirement
            light_message['max_offload'] = self.max_offloading_time
            light_message['content'] = 1
            light_message['cloud_processing'] = False
            task_message = light_message
            task_message['task_id'] = self.fog_task_id
            task_message['sending_time'] = time.time()
            self.fog_task_id += 1
            sending_message = bytes(json.dumps(task_message), "ascii")
            self.sock.send(sending_message)

    def sendMessage2(self):
        while True:
            time.sleep(self.middle_delay)
            middle_message = self.task_message1.copy()
            middle_message['task_id'] = 1
            middle_message['task_type'] = 'medium'
            middle_message['task_name'] = "medium"
            middle_message['time_requirement'] = self.middle_time_requirement
            middle_message['max_offload'] = self.max_offloading_time
            middle_message['content'] = 1
            middle_message['cloud_processing'] = False
            task_message = middle_message
            task_message['task_id'] = self.middle_task_id
            task_message['sending_time'] = time.time()
            self.middle_task_id += 1
            sending_message = bytes(json.dumps(task_message), "ascii")
            self.sock.send(sending_message)


    def sendMessage3(self):
        while True:
            time.sleep(self.heavy_delay)
            heavy_message = self.task_message1.copy()
            heavy_message['task_id'] = 1
            heavy_message['task_type'] = 'heavy'
            heavy_message['task_name'] = "heavy"
            heavy_message['time_requirement'] = self.heavy_time_requirement
            heavy_message['max_offload'] = self.max_offloading_time
            heavy_message['content'] = 1
            heavy_message['cloud_processing'] = True
            task_message = heavy_message
            task_message['task_id'] = self.cloud_task_id
            task_message['sending_time'] = time.time()
            self.cloud_task_id += 1
            sending_message = bytes(json.dumps(task_message), "ascii")
            self.sock.send(sending_message)



    def __init__(self, address, port):
        self.sock.connect((address, port))

        """"
        iThread = threading.Thread(target = self.sendMessage)
        iThread.daemon = True
        iThread.start()

        iThread1 = threading.Thread(target=self.sendMessage)
        iThread1.daemon = True
        iThread1.start()
        """

        try:
            if self.light_task_per_min > 0:
                _thread.start_new_thread(self.sendMessage, ())
            if self.middle_task_per_min > 0:
                _thread.start_new_thread(self.sendMessage2, ())
            if self.heavy_task_per_min > 0:
                _thread.start_new_thread(self.sendMessage3, ())
        except:
            print("Error: 无法启动线程")

        while True:

            data = self.sock.recv(1024)
            print(data)
            if not data:
                break;
            else:

                data = data.decode("ascii")
                print(data)
                unpacked_data = unpack(data)
                for data in unpacked_data:
                    message = json.loads(data)
                    if message['message_type'] == 'result' and int(message["sending_time"]) != 0:
                        task_type = message['task_type']
                        time_requirement = float(message['time_requirement'])
                        execution_time = float(message['execution_time'])
                        responding_time = time.time() - float(message['sending_time'])
                        waiting_time = responding_time - execution_time
                        offloading_times = message['offload_times']
                        process_by = message['process_by']
                        if waiting_time > time_requirement:
                            is_in_time = 0
                        else:
                            is_in_time = 1
                        print("Required_time: %f" % time_requirement)
                        print("Waiting_time: %f" % waiting_time)
                        print("In time or not: %d" % is_in_time)
                        print("responding_time (delay): %f" % responding_time)
                        print("offloading_times: %d" % offloading_times)
                        print("process_by: %s" % process_by)

                        if task_type == "light":
                            self.performance["light_num"] += 1
                            self.performance["light_delay"] += responding_time
                            self.performance["light_in_time"] += is_in_time
                            self.performance["light_avg_delay"] = self.performance["light_delay"]/self.performance["light_num"]
                            self.performance["light_in_time_rate"] = self.performance["light_in_time"]/self.performance["light_num"]
                        elif task_type == "medium":
                            self.performance["middle_num"] += 1
                            self.performance["middle_delay"] += responding_time
                            self.performance["middle_in_time"] += is_in_time
                            self.performance["middle_avg_delay"] = self.performance["middle_delay"] / self.performance[
                                "middle_num"]
                            self.performance["middle_in_time_rate"] = self.performance["middle_in_time"] / \
                                                                     self.performance["middle_num"]
                        elif task_type == "heavy":
                            self.performance["heavy_num"] += 1
                            self.performance["heavy_delay"] += responding_time
                            self.performance["heavy_in_time"] += is_in_time
                            self.performance["heavy_avg_delay"] = self.performance["heavy_delay"] / self.performance[
                                "heavy_num"]
                            self.performance["heavy_in_time_rate"] = self.performance["heavy_in_time"] / \
                                                                     self.performance["heavy_num"]
                        print(self.performance)
                        a = (self.performance["light_delay"] + self.performance["middle_delay"])/(self.performance["light_num"]+self.performance[
                                "middle_num"])
                        print(a)
                        print("")








if __name__=="__main__":
    client = Client('192.168.1.9', 10000)
