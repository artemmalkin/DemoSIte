const menu_auth = document.getElementById('menu-auth');

const getChat = Get('users.chat_id', `user_id=${urlParams.get('user_id')}`)
getChat.onload = function () {
    const response = JSON.parse(getChat.response)
    current_chat_id = response['users.chat_id']['chat_id']
}

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
                let get = Get('notifications.get', '', document.getElementById('notification-list'))
                get.onload = function () {
                    const response = JSON.parse(get.response)
                    document.getElementById('notification-list').innerHTML = response['notifications.get']
                };
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
        }
        if (count <= 99) {
            document.getElementById('notification-count').innerText = count !== 0 ? count : ''
        } else {
            document.getElementById('notification-count').innerText = '99+'
        }
    }
}


/**
 * Get the XmlHttpRequest.
 *
 * @param {string} methodName Name of the method like 'messages.search'.
 * @param {string} params Parameters for the method like 'user=1&content=hello'.
 * @param {HTMLElement} loadingElement HtmlElement which will be showing a loading gif inside himself while response is load.
 * @return {XMLHttpRequest} XMLHttpRequest.
 */
function Get(methodName, params = '', loadingElement = undefined) {
    let xml = new XMLHttpRequest();
    xml.open("GET", `/api/${methodName}?${params}`, true);
    xml.send(null);
    setTimeout(function () {
        if (xml.status === 0) {
            loadingElement.innerHTML = loading.outerHTML
        }
    }, 200)

    return xml;
}