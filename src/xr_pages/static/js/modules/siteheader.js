// import umbrella js

// import umbrella js
import u from 'umbrellajs/umbrella.esm.js'

const toggleHeaderBackground = () => {
    const scrollY = Math.max(document.documentElement.scrollTop || document.body.scrollTop || window.scrollTop || 0)
    if (scrollY > 5) {
        u("#header").addClass('is-scrolled')
    } else {
        u("#header").removeClass('is-scrolled')
    }
}
export const initSiteHeader = () => {
    toggleHeaderBackground()
    
    window.addEventListener('scroll', toggleHeaderBackground)

    u("#nav-toggle").on('click', function() {
        u("#nav").toggleClass("open")
        u('html').toggleClass("modal-open")
    })
}