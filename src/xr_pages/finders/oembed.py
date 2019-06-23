import requests
import logging
import uuid

from django.core import files
from wagtail.embeds.finders.oembed import OEmbedFinder
from xr_pages.models import VideoThumbnail

logger = logging.getLogger(__name__)


class YoutubePrivacyOEmbedFinder(OEmbedFinder):
    def find_embed(self, url, max_width=None):
        logger.debug("YoutubePrivacyOEmbedFinder for URL {}".format(url))

        # url = url.replace('youtube.com', 'youtube-nocookie.com')
        return_value = super().find_embed(url, max_width)

        # return {
        #     'title': oembed['title'] if 'title' in oembed else '',
        #     'author_name': oembed['author_name'] if 'author_name' in oembed else '',
        #     'provider_name': oembed['provider_name'] if 'provider_name' in oembed else '',
        #     'type': oembed['type'],
        #     'thumbnail_url': oembed.get('thumbnail_url'),
        #     'width': oembed.get('width'),
        #     'height': oembed.get('height'),
        #     'html': html,
        # }

        # Get thumbnail image from youtube
        thumbnail_image_request = requests.get(return_value["thumbnail_url"])

        if thumbnail_image_request.status_code == 200:
            # Use UUID as identifier for file
            thumbnail_id = uuid.uuid4().hex

            # Create model
            video_thumbnail = VideoThumbnail(
                uuid=thumbnail_id, source_url=return_value["thumbnail_url"]
            )
            video_thumbnail.thumbnail.save(
                name="{}{}".format(uuid, ".jpg"),
                content=files.File(thumbnail_image_request.content),
            )
            video_thumbnail.save()

            # Reference local thumbnail image in returned dictionary
            return_value["thumbnail_url"] = video_thumbnail.thumbnail.url

        # Return dictionary
        return return_value


embed_finder_class = YoutubePrivacyOEmbedFinder
