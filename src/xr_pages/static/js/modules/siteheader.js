// import umbrella js

// import umbrella js
import u from 'umbrellajs/umbrella.esm.js'

let scrollCache

const getScrollY = () => Math.max(
    window.pageYOffset,
    document.documentElement.scrollTop,
    document.body.scrollTop, 
    0
)

const securelyShowModals = () => {
    scrollCache = getScrollY()
    document.body.style.top = `-${scrollCache}px`
    u('body').addClass('modal-open')
}

const securelyHideModals = () => {
    u('body').removeClass('modal-open')
    document.body.style.top = ''
    document.body.scrollTop = scrollCache
    document.documentElement.scrollTop = scrollCache
    scrollCache = null
}

const toggleHeaderBackground = () => {
    const scrollY = getScrollY()
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
        window.ctx.modalOpen ? securelyHideModals() : securelyShowModals();
        window.ctx.modalOpen = !window.ctx.modalOpen
    })
}