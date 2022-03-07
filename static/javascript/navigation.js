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
            }

            break

        default:

            break

    }
});