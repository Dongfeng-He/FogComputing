1. Installation guide
Configure virtualbox:
sudo apt-get update
Install git:
sudo apt-get install git
Install pip3 on Ubuntu:
sudo apt-get install python3-pip
Install Redis on Ubuntu:
sudo apt-get install redis-server
redis-server (launch redis-server)
Insatll Redis in Python3:
pip3 install redis
Install Twisted:
pip3 install twisted
Insatll Celery in Python3:
pip3 install Celery   (can only install successfully in brige mode)

1.2 Launch AWS EC2 instance
follow: https://docs.aws.amazon.com/zh_cn/AWSEC2/latest/UserGuide/EC2_GetStarted.html?icmpid=docs_ec2_console
remind that when initialize the EC2 instance, you have to select name and value, and select an existing security group allow any IPs from port 22. Then down load the Key.pem.

2. Operation guide 
2.1 Configure fog server (Mac OS)
start redis at default port 6379:
cd redis-4.0.6
src/redis-server 
start redis at port 6380:
cd redis-4.0.6
src/redis-server --port 6380 &
start Celery service with tasks.py (using redis at 6379):
cd /Users/hedongfeng/PycharmProjects/fogcomputing3
celery -A tasks worker --loglevel=info
start Celery service with tasks6380.py (using redis at 6380):
cd /Users/hedongfeng/PycharmProjects/fogcomputing3
celery -A tasks6380 worker --loglevel=info
Run server.py
Run server6380.py
Run client.py

2.2 Configure fog server (Ubuntu OS)
start redis at default port 6379:
redis-server (no cd)
start Celery service with tasks.py (using redis at 6379):
cd FogComputing
celery -A tasks worker --loglevel=info
Run server.py

2.3 Connect to cloud server
Confirm the user name of different instances in https://docs.aws.amazon.com/zh_cn/AWSEC2/latest/UserGuide/AccessingInstancesLinux.html
Confirm public DNS in https://ap-southeast-2.console.aws.amazon.com/ec2/v2/home?region=ap-southeast-2#Instances:sort=availabilityZone
Make sure the key file is private: 
cd FogComputing
(chmod 400 /path/my-key-pair.pem)
chmod 400 fog_cloud.pem
Connect to the EC2 instance: 
(ssh -i /path/my-key-pair.pem user_name@public_dns_name)
cd FogComputing
ssh -i fog_cloud.pem ec2-user@ec2-52-63-235-224.ap-southeast-2.compute.amazonaws.com
ssh -i fog_cloud.pem ubuntu@ec2-54-206-45-203.ap-southeast-2.compute.amazonaws.com
(make sure you can open a website in Ubuntu, public DNS changes every time you restart the EC2 instance)

2.4 Configure cloud server (AWS linux)
sudo yum update
sudo yum install git
sudo yum insatll python36
sudo python3.6 -m pip install redis (sudo is necessary)
sudo python3.6 -m pip install celery

2.4.2 Configure cloud server (Ubuntu)
sudo apt-get update
Install pip3 on Ubuntu:
sudo apt-get install python3-pip
Install Redis on Ubuntu:
sudo apt-get install redis-server
Insatll Redis in Python3:
pip3 install redis
Install Twisted:
pip3 install twisted
Insatll Celery in Python3:
pip3 install Celery

2.5 Lauch cloud server
git clone https://github.com/Dongfeng-He/FogComputing.git
redis-server
cd FogComputing
celery -A tasks worker --loglevel=info
cd FogComputing
python3 cloud_server_simplified.py
Change the security group to allow traffic from my IP (every TCP)
Collect the public IP of the EC2 instance:
curl http://169.254.169.254/latest/meta-data/public-ipv4
Reminder:
restart the redis and celery in EC2 every time we access it, the public IP address will change every time we restart the EC2, you should open the cloud server first before opening fog server

2.6 Launch client
launch client.py for serveral times
launch client_for_cloud (compulsorily upload to cloud)


3. In-use files and functionalities
client.py
server.py
server6380.py
tasks.py 
task6380.py
functions.py 
communication.py 
message.py 
defer.py 	
		  
4. Functionalities
client.py

server.py

server6380.py

tasks.py 
define several task functions that can be called by server.py; client sends tasks to server, then server all the task handling functions to handle them

task6380.py


functions.py 
contain csvReader

message.py 
define various message structures)

communication.py (find_idle_port)

defer.py (called by tasks.py, asynchronous task handling)

5.逻辑
