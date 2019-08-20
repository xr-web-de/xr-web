import datetime
import logging
import re
import urllib
import os

from django.conf import settings
from django.core.files import File
from wagtail.embeds.finders.oembed import OEmbedFinder
from xr_embeds.models import VideoThumbnail


logger = logging.getLogger(__name__)


class YoutubePrivacyOEmbedFinder(OEmbedFinder):
    def find_embed(self, url, max_width=None):
        # logger.debug("YoutubePrivacyOEmbedFinder for URL {}".format(url))

        video_id_re = re.compile(
            r"(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/(watch\?v=|embed/|v/|.+\?v=)?(?P<id>[A-Za-z0-9\-=_]{11})"
        )

        match = video_id_re.match(self.youtube_url)

        if not match:
            logger.error(
                "YoutubePrivacyOEmbedFinder: Could not parse video_id from '{}'".format(
                    url
                )
            )
        video_id = match.group("id")

        check_url = "https://www.youtube-nocookie.com/watch?v={}".format(video_id)

        embed_dict = super().find_embed(check_url, max_width)
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

        # logger.debug('Trying to download thumbnail image from {}'.format(thumbnail_url))

        nocookie_url = "https://www.youtube-nocookie.com/embed/{}".format(video_id)
        embed_dict["nocookie_url"] = nocookie_url

        thumbnail_url = embed_dict["thumbnail_url"]

        video_thumbnail, created = VideoThumbnail.objects.get_or_create(
            thumbnail_url=thumbnail_url
        )

        thumbnail_cache_valid_until = video_thumbnail.last_updated + datetime.timedelta(
            seconds=settings.XR_EMBEDS_THUMBNAIL_CACHE_VALID_TIME
        )
        if datetime.datetime.now() < thumbnail_cache_valid_until:
            embed_dict["thumbnail_url"] = video_thumbnail.thumbnail.url
            return embed_dict

        # Get thumbnail image from youtube
        try:
            response = urllib.request.urlretrieve(thumbnail_url)
            #

            thumbnail_path = os.path.join(
                settings.MEDIA_ROOT,
                "video_thumbnails/{}.jpg".format(video_thumbnail.pk),
            )

            # logger.debug('YoutubePrivacyOEmbedFinger: saving thumbnail for {} as {}'.format(url, thumbnail_path))

            video_thumbnail.thumbnail.save(
                thumbnail_path, File(open(response[0], "rb"))
            )

            video_thumbnail.save()  # sets last_updated time

            # Reference local thumbnail image in returned dictionary
            embed_dict["thumbnail_url"] = video_thumbnail.thumbnail.url

            logger.debug(
                "YoutubePrivacyOEmbedFinger: Set thumbnail URL to {}".format(
                    embed_dict["thumbnail_url"]
                )
            )

        except (urllib.error.HTTPError, urllib.error.URLError) as e:
            logger.error(
                "YoutubePrivacyOEmbedFinder: HTTP error downloading thumbnail image for Youtube video {} from {}: {}".format(
                    url, thumbnail_url, e.code
                )
            )

        # Return dictionary
        return embed_dict


embed_finder_class = YoutubePrivacyOEmbedFinder
