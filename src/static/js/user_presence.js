window.onload = function(e) {
    var xmlHttp = new XMLHttpRequest();
    xmlHttp.open( "POST", "/api/user_presence/add", false );
    xmlHttp.send( "user={{ user_email }}" );
    return xmlHttp.responseText;
};

window.onbeforeunload = function(e) {
    var xmlHttp = new XMLHttpRequest();
    xmlHttp.open( "POST", "/api/user_presence/remove", false );
    xmlHttp.send( "user={{ user_email }}" );
    return xmlHttp.responseText;
};