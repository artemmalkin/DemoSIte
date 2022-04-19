
const menu_auth = document.getElementById('menu-auth');

updateNotifications()

menu_auth.addEventListener("click", function (event) {

    const target = event.target;

    switch (target.id) {

        case "notification-icon":

            let ntf_menu = document.getElementById('notification-menu')
            let ntf_list = document.getElementById('notification-list')
            if (ntf_menu.classList.contains('active')) {
                ntf_menu.classList.remove('active')
            } else {
                ntf_menu.classList.add('active')
                if (notifications.has_new) {
                    getNotifications(false, ntf_list)
                    notifications.has_new = false
                }
            }

            break

        default:

            break

    }
});

function getNotifications(page, ntf_list) {
            ntf_list = ntf_list ? ntf_list : document.getElementById("ntf-list")
            let get = page ? Get('notifications.get', `p=${page}`, ntf_list) : Get('notifications.get', '', ntf_list);
            get.onload = function () {
                updateNotifications()
                let response = JSON.parse(get.response)['notifications.get']

                ntf_list.innerHTML = page ? response.pagination : '';
                if (response.chat_ntf_count > 0) {
                    ntf_list.appendChild(createNtf('Новое сообщение!', '', 'Непрочитанных сообщений в чате: ' + response.chat_ntf_count))
                }
                response.base_ntf.forEach(function (ntf) {
                    ntf_list.appendChild(createNtf(ntf.title, ntf.date, ntf.content, ntf.is_read))
                })
                if (ntf_list.innerHTML === '') {
                    ntf_list.innerHTML = 'Уведомлений нет.'
                }
                if (!page) {
                    link = document.createElement('a')
                    link.innerText = 'Посмотреть все.'
                    link.href = response.see_more
                    ntf_list.appendChild(link)
                }
            }
        }

function updateNotifications() {
    let getNtfsCount = Get('notifications.count', '')
    getNtfsCount.onload = function () {
        const response = JSON.parse(getNtfsCount.response)
        const count = response['notifications.count']
        if (count === 0) {
            document.getElementById('notification-icon').setAttribute('src', '/static/icons/notification.svg')
        } else {
            document.getElementById('notification-icon').setAttribute('src', '/static/icons/notification-active.svg')
            notifications.has_new = true
        }
        if (count <= 99) {
            document.getElementById('notification-count').innerText = count !== 0 ? count : ''
        } else {
            document.getElementById('notification-count').innerText = '99+'
        }
    }
}

function addZero(i) {
    if (i < 10) {
        i = "0" + i
    }
    return i;
}

function createNtf(title, date, content, is_read) {
                            let ntf_item = document.createElement('div'); ntf_item.classList.add('ntf-item');
                            if (is_read) {
                                ntf_item.classList.add('secondary')
                            }
                            let ntf_title = document.createElement('div'); ntf_title.classList.add('ntf-title');
                            let ntf_date = document.createElement('div'); ntf_date.classList.add('ntf-date');
                            let ntf_content = document.createElement('div'); ntf_content.classList.add('ntf-content');
                            ntf_item.appendChild(ntf_title); ntf_item.appendChild(ntf_content);

                            date = date ? new Date(date) : '';

                            ntf_title.innerText = title
                            ntf_date.innerText = date ? `${date.toISOString().slice(0, 10)} ${date.getHours()}:${addZero(date.getMinutes())}` : '';
                            ntf_title.appendChild(ntf_date)
                            ntf_content.innerText = content

                            return ntf_item
                        }

