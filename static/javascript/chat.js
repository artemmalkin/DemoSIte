document.body.addEventListener("click", function(event) {

    const chat_window = document.getElementById('chat-window');

    let target = event.target.id;

    switch (target) {

        case "add-new-chat":

        chat_window.classList.add("act-new-chat");

        break

        case "close-new-chat":

        chat_window.classList.remove("act-new-chat");

        break

        default:

        break

    }

});

function Get(theUrl) {
            let xmlHttp = new XMLHttpRequest();
            xmlHttp.open( "GET", theUrl, false );
            xmlHttp.send( null );
            return xmlHttp.responseText;
        }