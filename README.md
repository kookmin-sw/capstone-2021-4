[![Work in Repl.it](https://classroom.github.com/assets/work-in-replit-14baed9a392b3a25080506f3b7b6d57f295ec2978f6f33ec97e36a161684cbe9.svg)](https://classroom.github.com/online_ide?assignment_repo_id=350588&assignment_repo_type=GroupAssignmentRepo)
# SomeCloud
<img width="218" alt="image" src="https://user-images.githubusercontent.com/3627483/119249954-c6a50b80-bbd7-11eb-8034-88d795425312.png">

### 프로잭트 소개

- AWS EC2 를 리셀링 하는 클라우드 컴퓨팅 프로젝트 입니다. SomeCloud 대시보드 상에서 클라우드 인스턴스를 추가할 수 있고, 키페어를 관리하고, 방화벽을 관리하고, 요금을 지불하는 시스템입니다.
- 키페어, 방화벽, 클라우드 인스턴스는 AWS EC2 자원을 활용합니다. SomeCloud 와 AWS 통신은 boto3 를 이용합니다.
- Flask 어플리케이션을 클라우드 서버에 배포하고, blue-green 배포를 지원합니다. (Rollback, Update 지원)

## DB schema, Backend blueprint
- https://docs.google.com/spreadsheets/d/1_fLHyhQrNPJ-qX4y3P5JEYWzwkZ2lrZBPZAP0lruyPg/edit?usp=sharing

### SomeCloud members

```
kimjenny, parkhuijoo
```

### Frontend
- static html 로 구현하였고, 반복적인 부분은 분리하고, 화면 전환이 쉽게 html 로 분리하였습니다.
- load.js 에서 상단, 좌측 메뉴 부분을 가져오도록 구현하였습니다.


### Backend
- Flask 로 html 을 Server side rendering 을 하고 있고, flask-app-blueprint 탬플릿을 기반으로 어플리케이션 서버를 작성하였습니다.
- 현재는 frontend 폴더에 있는 내용이 backend/app/project/templates, backend/app/project/static 에 반영된 상태입니다.

### branch
 
```
master
backend  - Dockerfile, Python Flask 코드
frontend - (legacy) 홈페이지 대시보드 페이지, 관리자 페이지
``` 

## Preview


<img width="1326" alt="image" src="https://user-images.githubusercontent.com/3627483/119249964-d1f83700-bbd7-11eb-8065-a085eb622b3c.png">

<img width="821" alt="image" src="https://user-images.githubusercontent.com/3627483/119249997-023fd580-bbd8-11eb-88b2-25ffdb11debd.png">

## SomeCloud Blue-green update / rollback 
[![Alt text](https://img.youtube.com/vi/Oy1Rli7alD0/0.jpg)](https://www.youtube.com/embed/Oy1Rli7alD0)
- Youtube link
