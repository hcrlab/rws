// window.onload = function(e) {
//     var xmlHttp = new XMLHttpRequest();
//     xmlHttp.open("POST", "/api/user_presence/add", false);
//     console.log("adding: " + "user=" + user + "&location=" + location);
//     xmlHttp.send("user=" + user + "&location=" + location);
//     return xmlHttp.responseText;
// };

// window.onbeforeunload = function(e) {
//     var xmlHttp = new XMLHttpRequest();
//     xmlHttp.open("POST", "/api/user_presence/remove", false );
//     console.log("removing: " + "user=" + user + "&location=" + location);
//     xmlHttp.send("user=" + user + "&location=" + location);
//     return xmlHttp.responseText;
// };