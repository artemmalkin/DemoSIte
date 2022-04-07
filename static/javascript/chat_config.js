let chat_data = {
    is_active: false,
    id: null,
    r_id: null,
    r_login: null,
    current_page: null,
    last_date: null,
    last_message_date: null,
};

function refresh_chat(user_id, DialogTabs=false, Notifications=false) {
    if (user_id) {
        const getChat = Get('chats.get_chat', `user_id=${user_id}`);
        getChat.onload = function () {
            const response = JSON.parse(getChat.response);
            chat_data = {
                is_active: true,
                id: response['chats.get_chat']['chat_id'],
                r_id: user_id,
                r_login: response['chats.get_chat']['recipient_login'],
                next_page: 1,
                last_date: null,
                last_message_date: null,
            };
            document.getElementById('chat-log').innerHTML = "";
            document.getElementById('current-user-name').innerText = chat_data.r_login;
            document.getElementById('current-user-name').href = '../profile/' + chat_data.r_id;


            getMessages(chat_data.next_page, chat_data.r_id, true);

            if (Notifications) {
                updateNotifications();
            }
            if (DialogTabs) {
                getDialogTabs();
            }
        };
    } else {
        getDialogTabs();
    }
}

