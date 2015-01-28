window.onbeforeunload = function(e) {
    var xmlHttp = new XMLHttpRequest();
    xmlHttp.open( "POST", "/api/user_presence/remove", false );
    xmlHttp.send( "user=IDENTIFIER_HERE" );
    return xmlHttp.responseText;
};