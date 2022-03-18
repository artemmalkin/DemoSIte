const chat_window = document.getElementById('chat-window');
const chat_list_items = document.getElementById('chat-list-items');
const chat_log = document.getElementById('chat-log');


let urlParams = new URLSearchParams(window.location.search);
let r_id = urlParams.get('user');
let current_page = 1;

getDialogs()
if (r_id) {
    getMessages(current_page, r_id)
}

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
            document.title = title

            const user_id = target.getAttribute("user_id");
            const url = `?user=${user_id}`;


            if (chat_window.classList.contains('act-new-chat')) {
                chat_window.classList.remove("act-new-chat");
                document.getElementById(`search-users-for-new-chat`).removeEventListener("keyup", searchUsers);
            }

            const getChat = Get(url + '&id')
            getChat.onload = function () {
                const response = JSON.parse(getChat.response)

                history.pushState({}, null, url);

                urlParams = new URLSearchParams(window.location.search);
                r_id = urlParams.get('user');
                current_chat_id = response.chat_id
                current_page = 1

                chat_log.innerHTML = ''
                getMessages(current_page, r_id)
                chat_log.scrollTo(0, chat_log.scrollHeight)

                getDialogs()
                updateNotifications()
                chat_window.classList.add('chat-active')
            }

            break

        case "send_button":

            const content = document.getElementById('input_message').value;
            socket.emit('send_message', {recipient: parseInt(r_id), content: content});
            document.getElementById('input_message').value = '';

            break

        case "page":

            const value = document.getElementById(`search-users-for-new-chat`).value;
            const getSearchUser = Get(`?search_user=${value}&p=${target.getAttribute('page')}`, document.getElementById(`search-user-result`))
            getSearchUser.onload = function () {
                document.getElementById(`search-user-result`).innerHTML = getSearchUser.responseText
            };

            break

        default:

            break

    }
});

chat_log.addEventListener('scroll', function (event) {
    if (chat_log.scrollTop === 0) {
        if (current_page) {
            getMessages(current_page, r_id)
        }

    }
})


function searchUsers(event = KeyboardEvent) {
    event.preventDefault();
    if (event.code === "Enter") {
        const value = document.getElementById(`search-users-for-new-chat`).value;
        const getSearchUser = Get(`?search_user=${value}&p=1`, document.getElementById(`search-user-result`))
        getSearchUser.onload = function () {
            document.getElementById(`search-user-result`).innerHTML = getSearchUser.responseText
        };
    }

}


function getMessages(page, r_id) {
    const getMessages = Get(`?messages&p=${page}&r_id=${r_id}`)
    getMessages.onload = function () {
        const response = JSON.parse(getMessages.response)
        const messages = response['messages']
        if (messages.length !== 0) {
            let scrollH = chat_log.scrollHeight
            for (let message in messages) {
                chat_log.prepend(createMessage(messages[message]))
            }

            chat_log.scrollTo(0, chat_log.scrollHeight - scrollH)
            current_page += 1
        } else {
            current_page = undefined
        }
    };
}

function createMessage(message) {
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

    if (me === message.sender.id) {
        message_item.classList.add('me');
    }

    message_content.innerText = message.content;
    message_content.className = 'message-content';

    message_item.appendChild(message_from);
    message_item.appendChild(message_content);

    return message_item
}


function getDialogs() {
    let getDialogs = Get('?dialogs')

    getDialogs.onload = function () {
        const response = JSON.parse(getDialogs.response)

        chat_list_items.innerHTML = ''

        for (let dialog in response.chats) {
            chat_list_items.append(createDialog(response.chats[dialog], r_id))
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
