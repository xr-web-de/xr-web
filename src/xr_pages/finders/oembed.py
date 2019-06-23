import logging
import uuid
import urllib
import os

from django.conf import settings
from django.core.files import File
from wagtail.embeds.finders.oembed import OEmbedFinder
from xr_pages.models import VideoThumbnail

logger = logging.getLogger(__name__)


class YoutubePrivacyOEmbedFinder(OEmbedFinder):
    def find_embed(self, url, max_width=None):
        # logger.debug("YoutubePrivacyOEmbedFinder for URL {}".format(url))

        url = url.replace("youtube.com", "youtube-nocookie.com")
        return_value = super().find_embed(url, max_width)
        thumbnail_url = return_value["thumbnail_url"]

        # logger.debug('Trying to download thumbnail image from {}'.format(thumbnail_url))

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
        try:
            response = urllib.request.urlretrieve(thumbnail_url)
            # Use UUID as identifier for file
            thumbnail_id = uuid.uuid4().hex

            # Create model
            video_thumbnail = VideoThumbnail(uuid=thumbnail_id, source_url=url)

            thumbnail_path = os.path.join(
                settings.MEDIA_ROOT, "video_thumbnails/{}.jpg".format(thumbnail_id)
            )

            # logger.debug('YoutubePrivacyOEmbedFinger: saving thumbnail for {} as {}'.format(url, thumbnail_path))

            video_thumbnail.thumbnail.save(
                thumbnail_path, File(open(response[0], "rb"))
            )

            video_thumbnail.save()

            # Reference local thumbnail image in returned dictionary
            return_value["thumbnail_url"] = video_thumbnail.thumbnail.url

            logger.debug(
                "YoutubePrivacyOEmbedFinger: Set thumbnail URL to {}".format(
                    return_value["thumbnail_url"]
                )
            )

        except urllib.error.HTTPError as e:
            logger.error(
                "YoutubePrivacyOEmbedFinger: HTTP error downloading thumbnail image for Youtube video {} from {}: {}".format(
                    url, thumbnail_url, e.code
                )
            )
        except urllib.error.URLError as e:
            logger.error(
                "YoutubePrivacyOEmbedFinger: URL error downloading thumbnail image for Youtube video {} from {}: {}".format(
                    url, thumbnail_url, e.reason
                )
            )

        # Return dictionary
        return return_value


embed_finder_class = YoutubePrivacyOEmbedFinder
