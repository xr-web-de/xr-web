// import umbrella js
import u from 'umbrellajs/umbrella.esm.js'

/*

*/

const applyFilterGroupChange = e => {
    console.log(e.target.value)
    window.location.href =
        e.target.value + '?d=' + document.getElementById('filter-by-date').value
}

const applyFilterTimespanChange = e => {
    console.log(e.target.value)
    window.location.href =
        document.getElementById('filter-by-groups').value +
        '?d=' +
        document.getElementById('filter-by-date').value
}

export const initEvents = () => {
    u('#filter-by-groups').on('change', applyFilterGroupChange),
        u('#filter-by-date').on('change', applyFilterTimespanChange)
}
