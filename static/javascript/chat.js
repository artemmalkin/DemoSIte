const chat_window = document.getElementById('chat-window');
const chat_log = document.getElementById('chat-log');

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

        case "page":

            const value = document.getElementById(`search-users-for-new-chat`).value;
            let get = Get(`?q=${value}&page=${target.getAttribute('page')}`, document.getElementById(`search-user-result`))
            get.onload = function () {
                document.getElementById(`search-user-result`).innerHTML = get.responseText
            };

            break

        default:

            break

    }
});

let messages_count = 50

chat_log.addEventListener('scroll', function (event) {
    if (chat_log.scrollTop === 0) {
        const urlParams = new URLSearchParams(window.location.search);
        const r_id = urlParams.get('c');

        messages_count += 50

        let get = Get(`?m=${messages_count}&r_id=${r_id}`)

        get.onload = function () {
            const response = JSON.parse(get.response)
            const data = response['data']
            const messages = response['messages'].reverse()
            let scrollH = chat_log.scrollHeight
            for (let message in messages) {
                chat_log.prepend(createMessage(data, messages[message]))
            }
            chat_log.scrollTo(0, chat_log.scrollHeight - scrollH)
        };
    }

})

function searchUsers(event = KeyboardEvent) {
    event.preventDefault();
    if (event.code === "Enter") {
        const value = document.getElementById(`search-users-for-new-chat`).value;
        let get = Get(`?q=${value}&page=1`, document.getElementById(`search-user-result`))
        get.onload = function () {
            document.getElementById(`search-user-result`).innerHTML = get.responseText
        };
    }

}

function createMessage(data, message) {
    let message_item = document.createElement('div');
    let message_from = document.createElement('a');
    let message_time = document.createElement('time')
    let message_content = document.createElement('div')

    message_item.className = 'message';

    message_from.className = 'message-from';
    message_from.href = `../profile/${message.sender.id}`;
    message_time.dateTime = message.date[0];
    message_time.innerText = ` ${message.date[1]}`;
    message_from.innerHTML = message.sender.login;

    message_from.appendChild(message_time)

    if (data.me === message.sender.id) {
        message_item.classList.add('me');
    }

    message_content.innerText = message.content;
    message_content.className = 'message-content';

    message_item.appendChild(message_from);
    message_item.appendChild(message_content);

    return message_item
}