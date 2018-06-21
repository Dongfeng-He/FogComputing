### 1. Brief Introduction
This is a fog computing application developed in Python using Twisted networking framework and Celery task queue.
As the Internet of Things technology develops, more and more smart devices are connected to the core network, generating a large amount of data every day. Using cloud computing to deal with this kind of data has led to two major issues: network congestion and high latency.
In order to solve this problem, a new computing model was proposed, that is, fog computing. The main idea of fog computing is to deploy some servers near the users to provide service with low latency. These servers are also called fog nodes.
When a fog node receives a lightweight task, it can process the task locally. When a fog node receives a middleweight task, it can collaborate with neighbour fog nodes to process the task. When a fog node receives a heavyweight task, it can upload the task to the cloud.
<div align=center><img width="350" height="350" src="https://cn.sharelatex.com/project/5b13e947e0ff0428a740b770/file/5b1b8c5c5130711b7481e85c"/></div>
The above figure shows the basic architecture of fog computing. This project can be divided into three parts: fog node application, cloud application and user application. User application can send tasks to fog nodes with different speeds, fog node application can process, offload or upload the tasks, cloud application can process the task and send the results back to fog nodes.

### 2. Deployment and Installation
The basic requirements for this project include Ubuntu operating system for fog nodes, AWS EC2 instance with Ubuntu operating system for cloud server and a smart device that supports Python3 script execution (e.g. an iPhone with Python3 IDE).

#### Deployment of fog node
The first step is the preparation of the Ubuntu OS for the fog node application. It is recommended to use VirtualBox to create a virtual machine with Ubuntu, because if you have successfully configure one fog node in a virtual machine, you can simply duplicate the virtual machine to create many virtual fog nodes quickly in one computer. If you use VirtualBox, it is important to set the network adapter of the virtual machines to `bridge mode` which can assign different IP addresses to different virtual machines.
The necessary softwares and libraries required for fog node include Git, Pip3, Redis, Twisted and Celery. You can use terminal to finish the installation.
Install git.
```javascript
sudo apt-get update
sudo apt-get install git
```
Install pip3.
```javascript
sudo apt-get install python3-pip
```
Install Redis database.
```javascript
sudo apt-get install redis-server
```
Install Redis Python library.
```javascript
pip3 install redis
```
Install Twisted networking framework.
```javascript
pip3 install twisted
```
Install Celery task queue.
```javascript
pip3 install Celery
```

#### Deployment of Cloud server
First step is to launch an AWS EC2 instance with Ubuntu OS.
Instruction to launch an AWS EC2 instance: https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/EC2_GetStarted.html?icmpid=docs_ec2_console
After launching an AWS EC2 instance, remember to record the public IP address and public DNS of the instance, which will be used to login your instance remotely in terminal. Also,  a PEM file will be downloaded, please store this file safely because it is the key to login your instance.
Set the directory to the folder where you store your PEM file.
```javascript
cd desktop
```
Protect your PEM file.
```javascript
chmod 400 my-key-pair.pem
```
Use and public IP and public DNS of your AWS EC2 instance and the PEM file to connect to your instance.
```javascript
ssh -i my-key-pair.pem user_name@public_dns_name
```
Now, your terminal should have connected to the cloud instance. Let's use this terminal to configure the environment of cloud server.
The configuration of cloud environment is similar to the configuration of fog environment.  You should install Git, Pip3, Redis, Redis Python package, Twisted and Celery in the instance.
```javascript
sudo apt-get update
sudo apt-get install git
sudo apt-get install python3-pip
sudo apt-get install redis-server
pip3 install redis
pip3 install twisted
pip3 install Celery
```

### 3. Start Service
Execute the fog node application, cloud application and user application to make it work.

#### Start Fog Node Application
The fog nodes running in the same LAN can collaborate with each other.
Clone this project to the fog node virtual machine.
```javascript
git clone https://github.com/Dongfeng-He/FogComputing.git
```
Open a new terminal window, launch Redis database. Redis is used as the broker and backend of Celery task queue.
```javascript
redis-server
```
Open a new terminal window, launch Celery task queue. `tasks` is the Python file where you define your tasks.
```javascript
cd FogComputing
celery -A tasks worker --loglevel=info --concurrency=1
```
Open a new terminal window, launch the fog node application. The fog node application is `server.py`.
```javascript
cd FogComputing
python3 server.py
```
#### Start Cloud Application
If you use terminal to connect to the cloud server. You should open three terminal windows. All terminals should connect to the cloud server before running the following commands.
Clone this project.
```javascript
git clone https://github.com/Dongfeng-He/FogComputing.git
```
Launch Redis database.
```javascript
redis-server
```
Use a new terminal window (connected to the cloud), launch Celery task queue.
```javascript
cd FogComputing
celery -A tasks worker --loglevel=info --concurrency=1
```
Use a new terminal window (connected to the cloud), launch the cloud application. The cloud application is `cloud_server_simplified.py.py`.
```javascript
cd FogComputing
python3 cloud_server_simplified.py
```
#### Start User Application
You can use a computer to execute the user application. Make sure that the computer you use to run the user application is within the same LAN as the fog nodes. The user application is `client_for_phone.py`. It is important to modify the IP in the following code of `client_for_phone.py` to the actual IP address of one of your fog node before you execute `client_for_phone.py`.
```javascript
client = Client('192.168.1.9', 10000)
```
Execute user application.
```javascript
git clone https://github.com/Dongfeng-He/FogComputing.git
cd FogComputing
python3 client_for_phone.py
```
Alternatively, you can execute the `client_for_phone.py` in your mobile phone with Python IDE. If you have an iPhone, you can install an App called `Python3IDE` and paste the code of `client_for_phone.py` to this App and execute it.







