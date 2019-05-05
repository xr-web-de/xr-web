/*
    this is where all the site magic gets started
*/

import { initSiteHeader } from './modules/siteheader.js'
import { initLocalGroups } from './pages/localgroups.js'
import { initEvents } from './pages/events.js'
import { initDatetimeWidget } from './modules/datetime_widget'

export const init = () => {
    window.ctx = {
        modalOpen: false,
    }

    initSiteHeader()

    initDatetimeWidget()

    const page = document.body.dataset.page || 'default'

    switch (page) {
        case 'eventlistpage':
            initEvents()
            break
        case 'eventgrouppage':
            initEvents()
            break
        case 'groups':
            initLocalGroups()
            break
        default:
            break
    }
}
