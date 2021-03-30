
function load(url, callback, renderTo, elementId) { 
    var xhr = new XMLHttpRequest();
    xhr.onreadystatechange = function() {
      if (xhr.readyState === 4) {
        callback(xhr.response, renderTo, elementId); 
      }
    }
    xhr.onerror = function() {
        alert('  web server 동작 확인해주어야함- localserver.sh')
    }
    xhr.open('GET', url, true);
    xhr.send('');
}

function render(response, renderTo, elementId) {  
    document.getElementById(elementId).insertAdjacentHTML(renderTo, response)    
}

function defaultCssLoader(view='default') {
    document.getElementsByTagName("head")[0].insertAdjacentHTML("beforeend", `<link rel='stylesheet' href='/static/app/css/views${view}.css'/>`) 
}

function renderByTag(response, tag, location) {
    document.getElementsByTagName(tag)[0].insertAdjacentHTML(location, response) 
}
 
var head = document.head;

function addScript(jsFiles) {
    // 얘는 배열을 인자로 받는 함수 녀석이다. 순서대로 js를 불러와주도록 하여 오류를 줄여준다.
    return new Promise((resolve, reject) => {
        var load = function(i) {
            var file = jsFiles[i];
            var script = document.createElement('script');
            script.type = 'text/javascript';
            script.onload = function() {
                i++;
                if(i === jsFiles.length) {
                    resolve();
                } else {
                     load(i);
                }
            }
            script.src = file;
            head.appendChild(script);
        };
        load(0);
    });
    
}

async function scriptLoader(view='default') {
    // same as <script src ='... // head
    // head area
    // 순서대로 script 실행.. https://developpaper.com/how-to-make-files-execute-sequentially-when-loading-javascript-files-dynamically/
    await addScript([
        "/static/vendor/modernizr/modernizr.js", 
        "/static/vendor/fastclick/fastclick.js",
        "/static/vendor/jquery/jquery.min.js", 
        "/static/vendor/chosen/chosen.jquery.min.js", 
        "/static/vendor/bootstrap/js/bootstrap.min.js",
        "/static/vendor/slider/js/bootstrap-slider.js", 
        "/static/vendor/filestyle/bootstrap-filestyle.min.js",
        "/static/vendor/animo/animo.min.js",
        "/static/vendor/sparklines/jquery.sparkline.min.js",
        "/static/vendor/slimscroll/jquery.slimscroll.min.js",
        "/static/vendor/store/store+json2.min.js",
        "/static/vendor/classyloader/js/jquery.classyloader.min.js",
        "/static/app/js/app.js", 
        `/static/app/js${view}.js`
    ])  
}

function init() { // custom init 
    // 반복적으로 쓰이는것들 매뉴, 왼쪽매뉴같은건 탬플릿화 
    // Default CSS
    load('/static/templates/_head.html', renderByTag, "head", "beforebegin")

    // Default Menu, footer
    load("/static/templates/_menu.html", render, "beforebegin" ,"content-area")
    load("/static/templates/_left-side.html", render, "beforebegin", 'content-area')
    load('/static/templates/_footer.html', render, "beforeend" , 'content-area')  


    // View CSS
    var pathname = window.location.pathname;  
    if (pathname == "") {
        console.log ("[console] Main css need to be defined.")
        // localhost:8080/   뷰가 아무것도 없으면 그냥 default.css, default.js 를 갖고온다.
        defaultCssLoader()
        scriptLoader()

    } else {
        // localhost:8080/{}/dashboard.html 일테고, dashboard 를 가져와서 css, js 를 갖고온다.
        // 뷰에 해당한 js는 맨 마지막에 호출해야 한다.
        // app/css/views/{pathname}
        // var filename = pathname.split('.')[0].split('/')
        // var parse_view = filename[filename.length - 1]
        defaultCssLoader(pathname)
        scriptLoader(pathname)
    } 
}
init() 