// import umbrella js
import u from 'umbrellajs/umbrella.esm.js'

export const initEmbeds = () => {
    u('.embed-load-button').each(function(node) {
        let wrapper = u(node.closest('.responsive-object'))
        let embed_url = wrapper.data('embed-url')

        if (!embed_url) {
            return
        }

        u(node).handle('click', async function() {
            const response = await fetch(embed_url, {
                credentials: 'omit',
            }).then(res => res.json())
            if (response['success'] === true) {
                wrapper.html(response['embed_html'])
            }
        })
    })
}
