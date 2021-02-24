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


// switchcontents

var tabButtons=document.querySelectorAll(".tabContainer .btn_group button");
var tabPanels=document.querySelectorAll(".tabContainer  .tabPanel");

function showPanel(panelIndex,colorCode) {
    tabButtons.forEach(function(node){
        node.style.backgroundColor="";
        node.style.color="";
    });
    tabButtons[panelIndex].style.backgroundColor=colorCode;
    tabButtons[panelIndex].style.color="white";
    tabPanels.forEach(function(node){
        node.style.display="none";
    });
    tabPanels[panelIndex].style.display="block";
    tabPanels[panelIndex].style.backgroundColor="white";
}

  



const selected = document.querySelector(".selected");
const optionsContainer = document.querySelector(".options-container");

const optionsList = document.querySelectorAll(".option");

selected.addEventListener("click", () => {
  optionsContainer.classList.toggle("active");
});

optionsList.forEach(o => {
  o.addEventListener("click", () => {
    selected.innerHTML = o.querySelector("label").innerHTML;
    optionsContainer.classList.remove("active");
  });
});
