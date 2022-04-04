const chat_window = document.getElementById('chat-window');
const chat_list_items = document.getElementById('chat-list-items');
const chat_log = document.getElementById('chat-log');

if (act === 'new') {
    document.body.classList.add('act-new-chat')
}

refresh_chat(urlParams.get("user_id"))

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

        case "show-chat-list":
            if (document.getElementById('chat-list').classList.contains('hidden-w')) {
                document.getElementById('chat-list').classList.remove("hidden-w");
                document.getElementById('show-chat-list').innerText = '<'
            } else {
                document.getElementById('chat-list').classList.add("hidden-w");
                document.getElementById('show-chat-list').innerText = '>'
            }


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
            chat_log.removeEventListener('scroll', onScrollgetMessages)
            refresh_chat(user_id)

            break

        case "send_button":

            const content = document.getElementById('input_message').value;

            socket.emit('send_message', {recipient: parseInt(chat_data.r_id), content: content});
            document.getElementById('input_message').value = '';

            break

        case "page":

            const value = document.getElementById(`search-users-for-new-chat`).value;

            const getSearchUser = Get('users.search', `username=${value}&p=${target.getAttribute('page')}`, document.getElementById(`search-user-result`))
            getSearchUser.onload = function () {
                document.getElementById(`search-user-result`).innerHTML = JSON.parse(getSearchUser.response)['users.search']
            };

            break

        default:

            break

    }
});

function onScrollgetMessages() {
    if (chat_log.scrollTop === 0) {
        if (chat_data.next_page) {
            getMessages(chat_data.next_page, chat_data.r_id)
        }
    }
}

document.getElementById(`search-message-line`).addEventListener("keyup", searchMessage);


function searchUsers(event = KeyboardEvent) {
    if (event.keyCode === 13) {
        const value = document.getElementById(`search-users-for-new-chat`).value;
        if (value) {
            const getSearchUser = Get('users.search', `username=${value}&p=1`, document.getElementById(`search-user-result`))
            getSearchUser.onload = function () {
                document.getElementById(`search-user-result`).innerHTML = JSON.parse(getSearchUser.response)['users.search']
            };
        }
    }
}

function searchMessage(event = KeyboardEvent) {
    if (event.keyCode === 13) {
        const value = document.getElementById(`search-message-line`).value;
        if (value) {
            document.body.classList.add('act-search-message')

            const getSearchMessage = Get('messages.search', `content=${value}&user_id=${chat_data.r_id}`, document.getElementById('search-message-result'))
            getSearchMessage.onload = function () {
                const response = JSON.parse(getSearchMessage.response)['messages.search']

                document.getElementById('search-message-result').innerHTML = ''

                for (let message in response) {
                    document.getElementById('search-message-result').appendChild(createMessage(response[message]))
                }
                if (document.getElementById('search-message-result').innerHTML === '') {
                    document.getElementById('search-message-result').innerHTML = 'Ничего не найдено.'
                }
            };
        }
    }
}

function getMessages(page, r_id, is_new = false) {
    const Messages = Get('messages.get', `p=${page}&user_id=${r_id}`);
    Messages.onload = function () {

        const response = JSON.parse(Messages.response);
        const messages = response['messages.get']['messages'];

        if (response['messages.get'].has_next) {
            chat_data.next_page += 1;
        } else {
            chat_data.next_page = null;
        }

        if (messages) {
            chat_window.classList.add('chat-active');

            if (messages.length !== 0) {
                const scrollH = chat_log.scrollHeight;

                for (let message in messages) {
                    let current_date = new Date(messages[message].date).toISOString().slice(0, 10)

                    if (chat_data.last_date !== null && current_date !== chat_data.last_date) {
                        chat_log.prepend(dateH(chat_data.last_date));
                    }
                    chat_log.prepend(createMessage(messages[message]))
                }
                if (chat_data.next_page === null) {
                    chat_log.prepend(dateH(chat_data.last_date));
                }

                if (!is_new) {
                    chat_log.scrollTo(0, chat_log.scrollHeight - scrollH);
                } else {
                    chat_log.scrollTo(0, chat_log.scrollHeight);
                    chat_log.addEventListener('scroll', onScrollgetMessages)
                    chat_data.last_message_date = messages[0].date.toISOString().slice(0, 10)
                }
            }
        }
    };
}

function dateH(datestr) {
    let h = document.createElement('h6');
    let p = document.createElement('p');
    p.innerText = datestr;
    h.appendChild(p)
    return h
}

function addZero(i) {
    if (i < 10) {
        i = "0" + i
    }
    return i;
}

function createMessage(message) {
    let message_item = document.createElement('div');
    let message_time = document.createElement('time')
    let message_content = document.createElement('div')

    message_item.className = 'message';

    let date = new Date(message.date)
    message_time.dateTime = message.date
    message_time.innerText = `${date.getHours()}:${addZero(date.getMinutes())}`;

    if (me === message.sender.id) {
        message_item.classList.add('me');
    }

    message_content.innerText = message.content;
    message_content.className = 'message-content';

    message_item.appendChild(message_content);
    message_item.appendChild(message_time);

    chat_data.last_date = date.toISOString().slice(0, 10)

    return message_item
}


function getDialogTabs() {
    let DialogsTabs = Get('chats.get_list')

    DialogsTabs.onload = function () {
        const response = JSON.parse(DialogsTabs.response)['chats.get_list']

        chat_list_items.innerHTML = ''

        for (const dialog in response['chats']) {
            chat_list_items.append(createDialogTab(response['chats'][dialog], chat_data.r_id))
        }
    }
}

function createDialogTab(chat, recipient_id) {
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



