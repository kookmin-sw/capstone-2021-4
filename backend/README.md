# Somecloud-backend
- 썸클라우드 백엔드 입니다. 탬플릿 안에 있는 html은 임시로 사용할 프론트엔드 파일이며, 프론트엔드 화면 개발에도 참고할 수 있습니다.

# Deploy on Local 

## 1. clone
```
git clone <this repo URL>
```

## 2. PIP
```
pip3 install -r requirements.txt --user
```

## 3. environment set
```
cp -rf .env.example .env
```

## 4. .env 작성
```
APP_SETTINGS=config.DevelopmentConfig
SECRET_KEY=<SECRET KEY>
MAIL_USERNAME=<your_google_email>
MAIL_PASSWORD=<your_google_password>
MAIL_DEFAULT_SENDER=
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=465
AWS_ACCESS_KEY_ID=<AWS Secret Key ID>
AWS_SECRET_ACCESS_KEY= < AWS Secret Access Key> 

#DB
SQLALCHEMY_DATABASE_URI=sqlite:///testcode.db
HOSTED_ZONE_ID=Z01531342TJHRLBMP4RYK
PUBLIC_IP_ADDR=3.36.213.43
```


## 5. DB Init / Migration
```
python3 main.py db init
python3 main.py db migrate 
python3 main.py db upgrade
```

## 6. DB 촉 데이터 추가
```
>> python3
Python 3.7.9 (default, Feb 18 2021, 03:10:35) 
[GCC 7.3.1 20180712 (Red Hat 7.3.1-12)] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> import initdb
```
```
>>> initdb.plan_add()
>>> initdb.admin_add("your_email@domain.com", "your_password")
>>> initdb.os_add()
>>> initdb.plan_add()
>>> initdb.app_add()
>>> initdb.add_app_script()
```

## 7. Redis 서버 시작
```
sh redis-server.sh 
```
## 8. worker 시작
```
cd app
rq worker
```
## 9 Run (Local)
```
python3 main.py runserver
```
## 10. Run
```
http://localhost:8080
```

# Deploy on Production Server
- Environment : AWS EC2 (Amazon Linux)
- CPU Core : 2Core
- RAM : 8GB
- OS : Amazon Linux
- 인터넷 연결이 필요함
- Python Ver:  3.7.9
- ELB (for 
- Route53 Domain

## 1. Install supervisord 
```
# sudo amazon-linux-extras install epel
# sudo yum install supervisor
```

## 2. Clone this repository
```
cd /home/ec2-user/
```

```
git clone https://github.com/kookmin-sw/capstone-2021-4/ -b backend
```


## 3. Install INI file to /etc/supervisord.d/flask.ini
```
[program:app]
directory=/home/ec2-user/capstone-2021-4/backend/app
command=/usr/local/bin/gunicorn main:app -b 0.0.0.0:8080
autostart=true
autorestart=true
stderr_logfile=/somecloud.err.log
stdout_logfile=/somecloud.out.log
```
## 4. Install Python
```
sudo yum install build-essential
sudo yum install gcc
sudo yum install python3-devel
```

## 5. Redis Install
```
sudo wget http://download.redis.io/redis-stable.tar.gz
sudo tar xvzf redis-stable.tar.gz
cd redis-stable/
sudo mkdir /etc/redis
sudo mkdir /var/lib/redis
sudo cp src/redis-server src/redis-cli /usr/local/bin/
sudo cp redis.conf /etc/redis
sudo wget https://raw.githubusercontent.com/saxenap/install-redis-amazon-linux-centos/master/redis-server
sudo mv redis-server /etc/init.d 
sudo chmod 755 /etc/init.d/redis-server

```
## 6. Reids server Start
```
sudo service redis-server start
```

## 7. Redis ping-pong test (check redis server)
```
redis-cli
127.0.0.1:6379>ping
PONG
127.0.0.1:6379>exit
```
## 8. Install Requirements 
```
cd /home/ec2-user/capstone-2021-4/backend/
sudo pip3 install -r requirements.txt # Must sudo, supervisord user = root
```
## 9. run worker
```
nohup rq worker &
```
## 10. Run Server
```
sudo service supervisord start
```

## 11. check supervisord service
```
sudo service supervisord status
```

## 12. check supervisord Log
```
tail -f /somecloud.out.log
```

## 13. create Load balancer

<img width="793" alt="image" src="https://user-images.githubusercontent.com/3627483/119249222-da4d7380-bbd1-11eb-8a5d-73a085f35e62.png">
- Select Application Loadbalancer

<img width="1015" alt="image" src="https://user-images.githubusercontent.com/3627483/119249246-efc29d80-bbd1-11eb-8a85-3c8c8d7023d1.png">

- Add Listener (HTTP, HTTPS)

<img width="982" alt="image" src="https://user-images.githubusercontent.com/3627483/119249256-05d05e00-bbd2-11eb-8874-169b8de189ac.png">

- Select VPC, Subnet ( 두 Subnet 은 Auto Public IP Assign 이 체크되어 있어야 함, 각 Subnet은 다른 Availability Zone에 속해야함 ) 
- Example) ap-northeast-2a ,ap-northeast-2b

<img width="589" alt="image" src="https://user-images.githubusercontent.com/3627483/119249369-f3a2ef80-bbd2-11eb-9cea-3e0e68f4801a.png">

- Add Certificate

<img width="1008" alt="image" src="https://user-images.githubusercontent.com/3627483/119249281-43cd8200-bbd2-11eb-9729-15b5797493de.png">
- Loadbalancer Security Group, 여기서는 80, 443포트만 추가되면 된다.
- Instance의  Security group 에서는 8080 포트가 Inbound rule 에 추가되어야 한다.


<img width="1003" alt="image" src="https://user-images.githubusercontent.com/3627483/119249383-12a18180-bbd3-11eb-8357-b6bede34fe1a.png">

- Target group설정(중요) - 8080 포트로 설정

<img width="1001" alt="image" src="https://user-images.githubusercontent.com/3627483/119249401-4da3b500-bbd3-11eb-871f-6d738422145b.png">

- SomeCloud 시스템이 설치된 EC2 인스턴스를 Target group에 추가한다 . (Register Target)






