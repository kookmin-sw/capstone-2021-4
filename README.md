# Somecloud-backend
- 썸클라우드 백엔드 입니다. 탬플릿 안에 있는 html은 임시로 사용할 프론트엔드 파일이며, 프론트엔드 화면 개발에도 참고할 수 있습니다.

## clone
```
git clone <this repo URL>
```

## PIP
```
pip3 install -r requirements.txt
```

## environment set
```
cp -rf .env.example .env
```

## .env 작성
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


## DB Init / Migration
```
python3 main.py db init
python3 main.py db migrate 
python3 main.py db upgrade
```

## Redis 서버 시작
```
redis-server
```
## worker 시작
```
cd app
rq worker
```
## Run (Local)
```
python3 main.py runserver
```

 