# Somecloud-backend
- 썸클라우드 백엔드 입니다. 탬플릿 안에 있는 html은 임시로 사용할 프론트엔드 파일이며, 프론트엔드 화면 개발에도 참고할 수 있습니다.

# Deploy on Local 

## 1. clone
```
git clone <this repo URL>
```

## 2. PIP
```
pip3 install -r requirements.txt
```

## 3. environment set
```
cp -rf .env.example .env
```

## 4. .env 작성
```
APP_SETTINGS=config.DevelopmentConfig
SECRET_KEY=<SECRET KEY>
MAIL_USERNAME=
MAIL_PASSWORD=
MAIL_DEFAULT_SENDER=
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=465
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=

# OAUTH
OAUTH_GOOGLE_CLIENTID=
OAUTH_GOOGLE_SECRETKEY=

#DB
SQLALCHEMY_DATABASE_URI=
```


## 5. DB Init / Migration
```
python3 main.py db init
python3 main.py db migrate 
python3 main.py db upgrade
```

## 6. Redis 서버 시작
```
redis-server
```
## 7. worker 시작
```
cd app
rq worker
```
## 8 Run (Local)
```
python3 main.py runserver
```

## docker를 통한 배포 방법
```
git clone <this repo URL>
```
## 환경변수 설정
- <3. 4.> 참고

## docker
```
docker-compose up --build
```
- -d 옵션으로 daemon으로 동작

## 실행
```
http://localhost:8080
```