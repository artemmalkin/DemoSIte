const menu_auth = document.getElementById('menu-auth');

menu_auth.addEventListener("click", function (event) {

    const target = event.target;

    switch (target.id) {

        case "notification-icon":

            let ntf_menu = document.getElementById('notification-menu')

            if (ntf_menu.classList.contains('active')) {
                ntf_menu.classList.remove('active')

            } else {
                ntf_menu.classList.add('active')
                let get = Get('?ntfs')
                document.getElementById('notification-list').innerHTML = '<img src="./static/loading.gif" alt="loading..."  width="50" />'
                get.onload = function () {
                 document.getElementById('notification-list').innerHTML = get.responseText
                };
            }

            break

        default:

            break

    }
});

function Get(theUrl) {
    let xml = new XMLHttpRequest();
    xml.open("GET", theUrl, true);
    xml.send(null);
    return xml;
}