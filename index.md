# SomeCloud 4조

## 프로젝트 소개 

- AWS Lightsail, Linode 와 같은 AWS Ec2 자원을 이용한 클라우드 컴퓨팅 서비스 입니다. 
- SomeCloud 대시보드 상에서 클라우드 인스턴스를 추가할 수 있고, 키페어를 관리하고, 방화벽을 관리하고, 크레딧을 추가해서 클라우드 사용 요금을 지불하는 시스템 입니다.
- 사용자는 SomeCloud 를 통해 클라우드 서버를 생성하면 그 서버에 Apache2, Flask, 등을 구동시킬 수 있고, 서버 콘솔 상태를 볼 수 있습니다.
- 방화벽을 통해 특정 포트를 닫고, 열고가 가능합니다.


## Abstract
- This project is cloud computing service based AWS EC2. on SomeCloud Dashboard, you can create cloud instance, manage keypair, manage firewall, and purchase credit than you pay cloud usage.
- When user create a cloud server through SomeCloud dashboard, you can operate apache2, flask, other application server.
- Using firewall manage, you can open / close port.

## 소개 영상
<iframe width="420" height="315" src="https://www.youtube.com/watch?v=XjVInLwz1MA" frameborder="0" allowfullscreen></iframe>

## 팀 소개 
- parkhuijoo 
- kimjayney 

## 사용법
- 회원가입을 하고 이메일 인증을 거칩니다.
- 로그인을 해서 키페어를 생성하고, 키페어를 다운로드 합니다. 
- 크레딧을 충전합니다. (최소 5000원) 
- 충전한 크레딧 5천원에 대해 관리자 승인이 완료되면 5천원 충전이 완료됩니다.
- Plan, OS, Hostname을 입력하여 클라우드를 생성합니다.
- 다운로드 받은 키페어를 가지고 Linux Shell 로 서버에 접속합니다.  
```
ssh -i id_rsa ubuntu@<Public IP>
```

## 기타
- 크레딧 충전 후 관리자 승인을 받아야 크레딧으로 인정됩니다.
