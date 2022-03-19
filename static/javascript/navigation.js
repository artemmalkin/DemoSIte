const title = document.title

const menu_auth = document.getElementById('menu-auth');

const loading = document.createElement('img')
loading.src = '../static/loading.gif'
loading.alt = 'loading...'
loading.width = 50
loading.classList.add('loading')

let url_for_icons

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
                let get = Get('?ntfs', document.getElementById('notification-list'))
                get.onload = function () {
                    document.getElementById('notification-list').innerHTML = get.responseText
                };
            }

            break

        default:

            break

    }
});

function updateNotifications() {
    let getNtfsCount = Get('?ntfs=count')
    getNtfsCount.onload = function () {
        let response = JSON.parse(getNtfsCount.response)
        let count = response.count_of_notifications
        if (count === 0) {
            document.getElementById('notification-icon').setAttribute('src', `${url_for_icons}/notification.svg`)
        } else {
            document.getElementById('notification-icon').setAttribute('src', `${url_for_icons}/notification-active.svg`)
        }
        if (count <= 99) {
            document.getElementById('notification-count').innerText = count != 0 ? count : ''
        } else {
            document.getElementById('notification-count').innerText = '99+'
        }
    }
}

function Get(theUrl, loading_element) {
    let xml = new XMLHttpRequest();
    xml.open("GET", theUrl, true);
    xml.send(null);
    setTimeout(function () {
        if (xml.status === 0) {
            loading_element.innerHTML = loading.outerHTML
        }
    }, 200)

    return xml;
}