// import umbrella js

// import umbrella js
import u from 'umbrellajs/umbrella.esm.js'

export const initSiteHeader = () => {
    console.log(u("#nav-toggle"))
    console.log(document.getElementById('nav-toggle'))

    u("#nav-toggle").on('click', function() {
        console.log('click')
        u("#nav").toggleClass("open")
    })
}