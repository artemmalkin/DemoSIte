const menu_auth = document.getElementById('menu-auth');

updateNotifications()

menu_auth.addEventListener("click", function (event) {

    const target = event.target;

    switch (target.id) {

        case "notification-icon":

            let ntf_menu = document.getElementById('notification-menu')

            if (ntf_menu.classList.contains('active')) {
                ntf_menu.classList.remove('active')
            } else {
                ntf_menu.classList.add('active')
                if (notifications.has_new) {
                    let get = Get('notifications.get', '', document.getElementById('notification-list'))
                    get.onload = function () {
                        document.getElementById('notification-list').innerHTML = JSON.parse(get.response)['notifications.get']
                    };
                    notifications.has_new = false
                }
            }

            break

        default:

            break

    }
});

function updateNotifications() {
    let getNtfsCount = Get('notifications.count', '')
    getNtfsCount.onload = function () {
        const response = JSON.parse(getNtfsCount.response)
        const count = response['notifications.count']
        if (count === 0) {
            document.getElementById('notification-icon').setAttribute('src', `${url_for_icons}/notification.svg`)
        } else {
            document.getElementById('notification-icon').setAttribute('src', `${url_for_icons}/notification-active.svg`)
            notifications.has_new = true
        }
        if (count <= 99) {
            document.getElementById('notification-count').innerText = count !== 0 ? count : ''
        } else {
            document.getElementById('notification-count').innerText = '99+'
        }
    }
}


