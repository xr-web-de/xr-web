import flatpickr from 'flatpickr'
import { German } from 'flatpickr/dist/l10n/de.js'

flatpickr.localize(German)

export const initDatetimeWidget = () => {
    flatpickr('.form-group--datetimeinput input', {
        enableTime: true,
        dateFormat: 'd.m.Y H:i',
        time_24hr: true,
    })
    flatpickr('.form-group--dateinput input', {
        enableTime: false,
        dateFormat: 'd.m.Y',
    })
}
