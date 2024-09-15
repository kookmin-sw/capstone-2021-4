var cloud_add = {}
 

cloud_add.selectPlan = function(node) {
    // node.parentNode.addClass("selected")
    var planList = document.getElementsByClassName("box-placeholder")
    for (var i = 0 ; i < planList.length; i++) {
        // planList[i].removeClass("selected")
        planList[i].classList.remove("selected")
    }
    
    console.log(node.parentNode.classList.add("selected"));
}