/*
    this is where all the site magic gets started
*/

import { initSiteHeader } from './modules/siteheader'

export const init = () => {
    console.log('Init')
    initSiteHeader();
}