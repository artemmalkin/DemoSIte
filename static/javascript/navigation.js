const menu_auth = document.getElementById('menu-auth');

const loading = document.createElement('img')
loading.src = '../static/loading.gif'
loading.alt = 'loading...'
loading.width = 50


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

function Get(theUrl, loading_element) {
    let xml = new XMLHttpRequest();
    xml.open("GET", theUrl, true);
    xml.send(null);
    loading_element.innerHTML = loading.outerHTML
    return xml;
}