
function load(url, callback, render_to) { 
    var xhr = new XMLHttpRequest();
    xhr.onreadystatechange = function() {
      if (xhr.readyState === 4) {
        callback(xhr.response, render_to);
      }
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
 
function init() { // custom init 
    // 반복적으로 쓰이는것들 매뉴, 왼쪽매뉴같은건 탬플릿화
    load("./templates/_menu.html", render, "wrapper" )
    load("./templates/_left-side.html", render, "wrapper")
    // 내용이 보일 영역처리
    load("./templates/_content-area.html", render, "wrapper")

    // 대시보드를 랜더링 해주는 함수
    route('dashboard')
}
init() 