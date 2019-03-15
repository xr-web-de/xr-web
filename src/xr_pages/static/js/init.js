/*
    this is where all the site magic gets started
*/

// import umbrella js
import u from 'umbrellajs/umbrella.esm.js'

export const init = () => {

    document.addEventListener("DOMContentLoaded", () => {
        u("html").removeClass("no-js")
    })    
}