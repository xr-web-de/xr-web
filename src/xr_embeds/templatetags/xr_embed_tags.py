from django import template
from wagtail.embeds import embeds
from wagtail.embeds.exceptions import EmbedException

from xr_embeds.services import get_or_create_cached_image_for_url

register = template.Library()


@register.simple_tag()
def get_embed(embed_url):
    try:
        embed = embeds.get_embed(embed_url)
        return embed
    except EmbedException:
        # silently ignore failed embeds, rather than letting them crash the page
        return ""


@register.simple_tag()
def get_cached_image(image_url):
    try:
        cached_image = get_or_create_cached_image_for_url(image_url)
        return cached_image.image
    except EmbedException:
        # silently ignore failed embeds, rather than letting them crash the page
        return ""
