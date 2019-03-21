/*
    this is where all the site magic gets started
*/

import { initSiteHeader } from './modules/siteheader.js'
import { initLocalGroups } from './pages/localgroups.js'
import { initEvents } from './pages/events.js'

export const init = () => {
    window.ctx = {
        modalOpen: false
    }

    initSiteHeader()

    const page = document.body.dataset.page || 'default'

    switch (page) {
    case 'events':
        initEvents()
        break
    case 'groups':
        initLocalGroups()
        break
    default: 
        break
    }
}