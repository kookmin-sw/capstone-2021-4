function deploy(name, cloudid){
    console.log(name, cloudid)
    call(`/cloud/deploy/${cloudid}/${name}`, function(response) {
        var response = JSON.parse(response)
        console.log(response)
        if (response.success == true) {
            alert('deploy request success  ')
        } else {
            alert(' other error ')
        }
    })
}
function rollback(cloudid) {
    call(`/action/${cloudid}/rollback')`, function(response) {
        var response = JSON.parse(response)
        console.log(response)
        if (response.success == true) {
            alert('deploy request success  ')
        } else {
            alert(' other error ')
        }
    })
}