// function deploy(name, cloudid){
//     console.log(name, cloudid)
//     call(`/cloud/deploy/${cloudid}/${name}`, function(response) {
//         var response = JSON.parse(response)
//         console.log(response)
//         if (response.success == true) {
//             alert('deploy request success  ')
//         } else {
//             alert(' other error ')
//         }
//     })
// }
function refreshIframe() {
    var ifr = document.getElementsByName('preview_web')[0];
    ifr.src = ifr.src;
}

function rollback(cloudid) {
    call(`/cloud/action/${cloudid}/rollback`, function(response) {
        var response = JSON.parse(response)
        console.log(response)
        if (response.success == true) {
            alert('rollback request success  ')
        } else {
            alert(' other error ')
        }
    })
}

function update(cloudid) {
    call(`/cloud/action/${cloudid}/update`, function(response) {
        var response = JSON.parse(response)
        console.log(response)
        if (response.success == true) {
            alert('update request success  ')
        } else {
            alert(' other error ')
        }
    })
}
