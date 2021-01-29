var price_view = {}

price_view.test_function = function() {
    console.log("Test function")
}
price_view.test_function2 = function(a,b) {
    console.log(`test func with parameter ${a}, ${b}`)
}
// price_view.html 에서 <button onclick="price_view.test_function2(4,3)">버튼테스트</button> 부분이 바로 위 함수 호출하는거임

price_view.move_view = function() {
    route('cloud_list') // 클라우드  리스트로 화면 이동
}