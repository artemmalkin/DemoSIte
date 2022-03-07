const chat_window = document.getElementById('chat-window');
const chat_log = document.getElementById('chat-log')

chat_window.addEventListener("click", function (event) {

    const target = event.target;

    switch (target.id) {

        case "add-new-chat":

            chat_window.classList.add("act-new-chat");
            document.getElementById(`search-users-for-new-chat`).addEventListener("keyup", searchUsers);

            break

        case "close-new-chat":

            chat_window.classList.remove("act-new-chat");
            document.getElementById(`search-users-for-new-chat`).removeEventListener("keyup", searchUsers);

            break

        case "user-item":

            const url = `?c=${target.getAttribute("user_id")}`;
            const user_id = target.getAttribute("user_id");
            if (chat_window.classList.contains('act-new-chat')) {
                chat_window.classList.remove("act-new-chat");
                document.getElementById(`search-users-for-new-chat`).removeEventListener("keyup", searchUsers);
                document.getElementById('chat-list-items').prepend(target);
                socket.emit('new_chat', {recipient: parseInt(user_id)});
            }

            target.classList.add("current");


            setTimeout(() => {
                window.location.href = url
            }, 200)

            break

        case "send_button":

            const recipient = document.getElementById('chat-input').getAttribute('send_to')
            const content = document.getElementById('input_message').value;
            socket.emit('send_message', {recipient: parseInt(recipient), content: content});
            document.getElementById('input_message').value = '';

            break

        default:

            break

    }
});

function searchUsers(event = KeyboardEvent) {
    event.preventDefault();
    if (event.code === "Enter") {
        const value = document.getElementById(`search-users-for-new-chat`).value;

        const url = `?q=${value}`;

        document.getElementById(`search-user-result`).innerHTML = Get(url)
    }

}

function Get(theUrl) {
    let xmlHttp = new XMLHttpRequest();
    xmlHttp.open("GET", theUrl, false);
    xmlHttp.send(null);
    return xmlHttp.responseText;
}

function createMessage(data) {
    let message = document.createElement('div');
    let message_from = document.createElement('a');
    let message_time = document.createElement('time')
    let message_content = document.createElement('div')

    message.className = 'message';

    message_from.className = 'message-from';
    message_from.href = `../profile/${data.sender.id}`;
    message_time.dateTime = data.date[0];
    message_time.innerText = ` ${data.date[1]}`;
    message_from.innerHTML = data.sender.login;
    message_from.appendChild(message_time)

    if (data.me) {
        message.classList.add('me');
    }

    message_content.innerText = data.content;
    message_content.className = 'message-content';

    message.appendChild(message_from);
    message.appendChild(message_content);
    chat_log.append(message);
    chat_log.scrollTo(0, chat_log.scrollHeight);
}
