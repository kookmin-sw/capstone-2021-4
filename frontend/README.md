[![Work in Repl.it](https://classroom.github.com/assets/work-in-replit-14baed9a392b3a25080506f3b7b6d57f295ec2978f6f33ec97e36a161684cbe9.svg)](https://classroom.github.com/online_ide?assignment_repo_id=350588&assignment_repo_type=GroupAssignmentRepo)
# Somecloud Front-end

썸클라우드 프론트엔드 코드-모듈화 뼈대

## Usage
- clone
```
git clone https://github.com/kookmin-sw/capstone-2021-4/ -b frontend
```

- run
```
sh localserver.sh
```

- 안될 시
```
python3 -m pip install http.server 
```

## 디렉터리 구조
```
app
- css
  - views - ./views 에 해당하는(cloud_add, cloud_list ...) 파일 이름과 일치
    - cloud_add.css
    - cloud_list.css
- img
- js
  - cloud_add.js
  - cloud_list.js
  - dashboard.js - ./views 에 해당하는(cloud_add, cloud_list ...) 파일 이름과 일치
pages 
- 로그인, 인트로 페이지 파일
templates
- _content-area - 콘텐츠 영역 렌더링하는데 필요한 파일
- _left-side - 왼쪽 매뉴 영역
- _menu - 상단 매뉴 영역
- _right-side - 아직 사용 안하지만 냅둔파일
vendor
- Wintermin 내부 라이브러리 파일들
views
- cloud_add.html 클라우드 추가 화면
- cloud_list.html 클라우드 리스트
- dashboard.html 대시보드 화면
localserver.sh - 로컬 웹 서버 실행 파일
refer_* - 개발할 때 참고하는 파일 ( 아이콘, 버튼, 영역, 등등)
```

## 커밋 / 푸쉬 요령 - ex) cloud_add.html 완성 후 여기에 커밋 할 때
``` 
❯ git status
On branch frontend
Your branch is up to date with 'origin/frontend'.

nothing to commit, working tree clean
```
- git status 를 치고 현재 브랜치가 `frontend` 브랜치인지 확인한다. 

```
git add views/cloud_add.html
git add app/css/views/cloud_add.css
git commit -m "cloud_add.html 에서 버튼을 추가하고, css디자인을 입힘"
git push origin frontend
```
- 파일마다 꼭 할 필요는 없지만 해주면 좋고, 최소한 커밋할 때 어떤걸 했는지 커밋메세지로 남기는것이 중요함.

## current status
- 현재는 backend/app/project/templates 에 반영된 상태. 
- 백엔드 templates 에는 여기에 있던 views/html file들이 들어가고
- 백엔드 static 에는 app/에 있던 css&js 파일이 들어간다. 
