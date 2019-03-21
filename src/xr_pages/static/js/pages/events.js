// import umbrella js
import u from 'umbrellajs/umbrella.esm.js'

/*

*/

const applyFilter = e => {
    console.log(e.target.value)
    window.location.href = e.target.value;
}

export const initEvents = () => {
    u('#filter-by-groups').on('change', applyFilter)
}