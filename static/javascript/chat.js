const chat_window = document.getElementById('chat-window');
const chat_list_items = document.getElementById('chat-list-items');
const chat_log = document.getElementById('chat-log');

if (act === 'new') {
    document.body.classList.add('act-new-chat')
}
getDialogs()
if (r_id) {
    getMessages(current_page, r_id)
}

chat_window.addEventListener("click", function (event) {

    const target = event.target;

    switch (target.id) {

        case "add-new-chat":

            urlParams.set('act', 'new')
            history.pushState({}, null, `?${urlParams.toString()}`);

            document.body.classList.add("act-new-chat");
            document.getElementById(`search-users-for-new-chat`).addEventListener("keyup", searchUsers);

            break

        case "close-new-chat":

            urlParams.delete('act')
            history.pushState({}, null, `?${urlParams.toString()}`);

            document.body.classList.remove("act-new-chat");
            document.getElementById(`search-users-for-new-chat`).removeEventListener("keyup", searchUsers);

            break

        case "close-search-message":

            document.body.classList.remove("act-search-message");

            break

        case "user-item":
            document.title = title

            const user_id = target.getAttribute("user_id");

            urlParams.set('user_id', user_id)
            history.pushState({}, null, `?${urlParams.toString()}`);

            if (chat_window.classList.contains('act-new-chat')) {
                chat_window.classList.remove("act-new-chat");
                document.getElementById(`search-users-for-new-chat`).removeEventListener("keyup", searchUsers);
            }

            const getChat = Get('users.chat_id', `user_id=${user_id}`)
            getChat.onload = function () {
                const response = JSON.parse(getChat.response)

                r_id = user_id;
                current_chat_id = response['users.chat_id']['chat_id']
                current_page = 1

                chat_log.innerHTML = ''

                getMessages(current_page, r_id)
                getDialogs()
                updateNotifications()
            }

            break

        case "send_button":

            const content = document.getElementById('input_message').value;

            socket.emit('send_message', {recipient: parseInt(r_id), content: content});
            document.getElementById('input_message').value = '';

            break

        case "page":

            const value = document.getElementById(`search-users-for-new-chat`).value;

            const getSearchUser = Get('users.search', `username=${value}&p=${target.getAttribute('page')}`, document.getElementById(`search-user-result`))
            getSearchUser.onload = function () {
                const response = JSON.parse(getSearchUser.response)

                document.getElementById(`search-user-result`).innerHTML = response['users.search']
            };

            break

        default:

            break

    }
});

chat_log.addEventListener('scroll', function () {
    if (chat_log.scrollTop === 0) {
        if (current_page) {
            getMessages(current_page, r_id)
        }
    }
})
document.getElementById(`search-message-line`).addEventListener("keyup", searchMessage);


function searchUsers(event = KeyboardEvent) {
    if (event.keyCode === 13) {
        const value = document.getElementById(`search-users-for-new-chat`).value;
        if (value) {
            const getSearchUser = Get('users.search', `username=${value}&p=1`, document.getElementById(`search-user-result`))
            getSearchUser.onload = function () {
                const response = JSON.parse(getSearchUser.response)

                document.getElementById(`search-user-result`).innerHTML = response['users.search']
            };
        }
    }
}

function searchMessage(event = KeyboardEvent) {
    if (event.keyCode === 13) {
        const value = document.getElementById(`search-message-line`).value;
        if (value) {
            document.body.classList.add('act-search-message')

            const getSearchMessage = Get('messages.search', `content=${value}&user_id=${r_id}`, document.getElementById('search-message-result'))
            getSearchMessage.onload = function () {
                const response = JSON.parse(getSearchMessage.response)

                document.getElementById('search-message-result').innerHTML = ''

                for (let message in response['messages.search']) {
                    document.getElementById('search-message-result').appendChild(createMessage(response['messages.search'][message]))
                }
                if (document.getElementById('search-message-result').innerHTML === '') {
                    document.getElementById('search-message-result').innerHTML = 'Ничего не найдено.'
                }
            };
        }
    }
}


function getMessages(page, r_id) {
    const getMessages = Get('messages.get', `p=${page}&user_id=${r_id}`)
    getMessages.onload = function () {
        const response = JSON.parse(getMessages.response)
        const messages = response['messages.get']['messages']
        if (messages) {
            chat_window.classList.add('chat-active')
            if (messages.length !== 0) {
                const scrollH = chat_log.scrollHeight

                for (let message in messages) {
                    chat_log.prepend(createMessage(messages[message]))
                }

                chat_log.scrollTo(0, chat_log.scrollHeight - scrollH)
                current_page += 1
            } else {
                current_page = undefined
            }
        }
    };
}

function createMessage(message) {
    let message_item = document.createElement('div');
    let message_time = document.createElement('time')
    let message_content = document.createElement('div')

    message_item.className = 'message';

    message_time.dateTime = message.date[0];
    message_time.innerText = ` ${message.date[1]}`;

    if (me === message.sender.id) {
        message_item.classList.add('me');
    }

    message_content.innerText = message.content;
    message_content.className = 'message-content';

    message_item.appendChild(message_content);
    message_item.appendChild(message_time);

    return message_item
}


function getDialogs() {
    let getDialogs = Get('chats.get')

    getDialogs.onload = function () {
        const response = JSON.parse(getDialogs.response)

        chat_list_items.innerHTML = ''

        for (const dialog in response['chats.get']['chats']) {
            chat_list_items.append(createDialog(response['chats.get']['chats'][dialog], r_id))
        }
    }
}

function createDialog(chat, recipient_id) {
    let user_item = document.createElement('div');
    let a = document.createElement('a');

    user_item.classList.add('user-item')

    if (chat.recipient.id === parseInt(recipient_id)) {
        user_item.classList.add('current')
    }

    user_item.id = 'user-item'
    user_item.setAttribute('user_id', `${chat.recipient.id}`)

    a.href = `../profile/${chat.recipient.id}`
    a.innerText = chat.recipient.login
    if (chat.notifications) {
        a.innerText += ` (+${chat.notifications})`
    }

    user_item.appendChild(a)

    return user_item
}
