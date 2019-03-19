// import umbrella js

// import umbrella js
import u from 'umbrellajs/umbrella.esm.js'

export const initSiteHeader = () => {
    u("#nav-toggle").on('click', function() {
        u("#nav").toggleClass("open")
    })
}