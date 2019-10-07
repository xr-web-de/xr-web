import logging
import re

import requests
from bs4 import BeautifulSoup
from django.core.exceptions import ImproperlyConfigured
from wagtail.embeds.exceptions import EmbedNotFoundException
from wagtail.embeds.finders.base import EmbedFinder
from wagtail.embeds.finders.oembed import OEmbedFinder
from wagtail.embeds.oembed_providers import youtube

from xr_embeds.services import sandbox_embed_html

logger = logging.getLogger(__name__)


youtube_nocookie = {
    "endpoint": "https://www.youtube.com/oembed",
    "urls": [
        r"^http(?:s)?://youtu\.be/.+$",
        r"^http(?:s)?://m\.youtube(?:-nocookie)?\.com/index.+$",
        r"^http(?:s)?://(?:[-\w]+\.)?youtube(?:-nocookie)?\.com/watch.+$",
        r"^http(?:s)?://(?:[-\w]+\.)?youtube(?:-nocookie)?\.com/v/.+$",
        r"^http(?:s)?://(?:[-\w]+\.)?youtube(?:-nocookie)?\.com/user/.+$",
        r"^http(?:s)?://(?:[-\w]+\.)?youtube(?:-nocookie)?\.com/[^#?/]+#[^#?/]+/.+$",
        r"^http(?:s)?://(?:[-\w]+\.)?youtube(?:-nocookie)?\.com/profile.+$",
        r"^http(?:s)?://(?:[-\w]+\.)?youtube(?:-nocookie)?\.com/view_play_list.+$",
        r"^http(?:s)?://(?:[-\w]+\.)?youtube(?:-nocookie)?\.com/playlist.+$",
    ],
}


class YoutubeNoCookieOEmbedFinder(OEmbedFinder):
    def __init__(self, providers=None, options=None):
        if providers is None:
            providers = [youtube, youtube_nocookie]

        if providers != [youtube, youtube_nocookie]:
            raise ImproperlyConfigured(
                "The YoutubeNoCookieOEmbedFinder only operates "
                "on the youtube_nocookie provider"
            )

        super().__init__(providers=providers, options=options)

    def find_embed(self, url, max_width=None):
        video_id_re = re.compile(
            r"(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/"
            r"(watch\?v=|embed/|v/|.+\?v=)?(?P<id>[A-Za-z0-9\-=_]{11})"
        )
        match = video_id_re.match(url)

        if not match:
            logger.error(
                "YoutubeNoCookieOEmbedFinder: "
                "Could not parse video_id from '{}'".format(url)
            )
            raise EmbedNotFoundException

        video_id = match.group("id")

        check_url = "https://www.youtube-nocookie.com/watch?v={}".format(video_id)
        embed_dict = super().find_embed(check_url, max_width)
        # embed_dict["url"] = url

        html = embed_dict["html"]
        html = sandbox_embed_html(check_url, html)
        embed_dict["html"] = html

        return embed_dict


class UmapEmbedFinder(EmbedFinder):
    def accept(self, url):
        match = re.compile(
            r"^https://umap\.openstreetmap\.de/de/map/(?P<umap_slug>[-a-zA-Z]+)_(?P<umap_id>\d+)"
        ).match(url)
        if match and match.group("umap_id"):
            return True
        return False

    def find_embed(self, url, max_width=None):
        match = re.compile(
            r"^https://umap\.openstreetmap\.de/de/map/(?P<umap_slug>[-a-zA-Z]+)_(?P<umap_id>\d+)"
        ).match(url)

        if not match:
            logger.error(
                "UmapEmbedFinder: " "Could not parse umap_id from '{}'".format(url)
            )
            # raise EmbedNotFoundException
        umap_page = requests.get(url)
        soup = BeautifulSoup(umap_page.content, "html.parser")
        title = soup.find("head").find("title").text
        html = sandbox_embed_html(url, '<iframe src="{}"></iframe>'.format(url))

        embed_dict = {
            "title": title,
            "author_name": "",
            "provider_name": "Umap",
            "type": "rich",
            "thumbnail_url": None,
            "width": 640,
            "height": 360,
            "html": html,
        }
        return embed_dict
