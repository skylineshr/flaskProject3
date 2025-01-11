function getTime() {
    var now = new Date(); // get current time
    var hours = now.getHours(); // get hours
    var minutes = now.getMinutes(); // get minutes
    var seconds = now.getSeconds(); // get seconds

    //formatting time
    hours = hours < 10 ? '0' + hours : hours;
    minutes = minutes < 10 ? '0' + minutes : minutes;
    seconds = seconds < 10 ? '0' + seconds : seconds;

    //update time to the page with id match
    document.getElementById('time-element').textContent = hours + ':' + minutes + ':' + seconds;
}

//update once per second
setInterval(getTime, 1000);

//onload after finish loading page
window.onload = function () {
    getTime();
}