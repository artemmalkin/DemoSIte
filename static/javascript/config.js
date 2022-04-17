const title = document.title

// loading anim element
const loading = document.createElement('img')
loading.src = '../static/loading.gif'
loading.width = 50
loading.classList.add('loading')

let urlParams = new URLSearchParams(window.location.search);

let notifications = {
    has_new: true,
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