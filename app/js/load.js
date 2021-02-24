
function load(url, callback, render_to) { 
    var xhr = new XMLHttpRequest();
    xhr.onreadystatechange = function() {
      if (xhr.readyState === 4) {
        callback(xhr.response, render_to); 
      }
    }
    xhr.onerror = function() {
        alert('  web server 동작 확인해주어야함- localserver.sh')
    }
    xhr.open('GET', url, true);
    xhr.send('');
}

function render(response, render_to) {
    var area = document.getElementById(render_to) 
    area.innerHTML += response
}

function content_render(response) { // section 부분 렌더링 해줌
    var area = document.getElementById("content-area")
    area.innerHTML = response
}

function route(router_name) {
    // html 가져오기
    load(`./views/${router_name}.html`, content_render )
    // 동적으로 js 와 css를 로딩처리해줌 (모듈화)
    // js loader (RequireJS)
    require([router_name])
    // css loader
    var cssloader = document.getElementById("dLoaderCSS") 
    cssloader.setAttribute("href", `app/css/views/${router_name}.css`)
}
window.onhashchange = function() {
    if (window.location.hash.indexOf("-") > 0) {
        // do nothing
        // cloudadd.html처럼 안에서 a 태그를 통해 section을 이동시키고 싶을 때 go-plan 형식으로 해야하며, '-' 가 반드시 들어가게
    } else {
        routing()
    } 
}
function routing() {
    if(window.location.hash) { 
        var hash = window.location.hash.substring(1); // #asdf 값을 가져온다, asdf
        route(hash) //hash값이 dashboard이면 route('dashboard') 로 라우팅 시도
    } else {
        route('dashboard') // 기본적으로 대시보드가 보이게
    }  
}

function init() { // custom init 
    // 반복적으로 쓰이는것들 매뉴, 왼쪽매뉴같은건 탬플릿화
    load("./templates/_menu.html", render, "wrapper" )
    load("./templates/_left-side.html", render, "wrapper")
    // 내용이 보일 영역처리
    load("./templates/_content-area.html", render, "wrapper")
    routing()
}
init() 