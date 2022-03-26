const title = document.title

// loading anim element
const loading = document.createElement('img')
loading.src = '../static/loading.gif'
loading.width = 50
loading.classList.add('loading')

let url_for_icons
let urlParams = new URLSearchParams(window.location.search);
let act = urlParams.get('act')