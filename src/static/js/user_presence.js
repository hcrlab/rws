// TODO(csu): remove redundancy between these two

window.onload = function(e) {
    $.post("/api/user_presence/add", {
        user: currentUser,
        location: currentLocation
    },
    function(data, status) {
        console.log("Data: " + data + "\nStatus: " + status);
    });
};

window.onbeforeunload = function(e) {
    $.post("/api/user_presence/remove", {
        user: currentUser,
        location: currentLocation
    },
    function(data, status) {
        console.log("Data: " + data + "\nStatus: " + status);
    });
};