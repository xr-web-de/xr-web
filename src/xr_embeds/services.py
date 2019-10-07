import datetime
import logging
import urllib
from urllib.parse import urlparse, urlunparse, parse_qs, urlencode

from bs4 import BeautifulSoup
from django.core.files import File
from django.utils import timezone

from xr_embeds.models import CachedImage


logger = logging.getLogger(__name__)


def get_or_create_cached_image_for_url(url):
    cached_image_qs = CachedImage.objects.filter(original_url=url)

    if cached_image_qs.exists():
        cached_image = cached_image_qs.get()
        if cached_image.last_updated > timezone.now() - datetime.timedelta(days=1):
            return cached_image

    ext = url.split(".")[-1]
    if ext not in ["jpg", "jpeg", "png", "gif", "svg"]:
        raise ValueError('Invalid file extension "{}".'.format(ext))

    # Get image from url
    try:
        response = urllib.request.urlretrieve(url)
    except (urllib.error.HTTPError, urllib.error.URLError) as e:
        logger.error("Error downloading image from {}: {}".format(url, e))

    cached_image, created = CachedImage.objects.get_or_create(original_url=url)

    file_name = "{}.{}".format(cached_image.id, ext)

    cached_image.image.save(file_name, File(open(response[0], "rb")))

    cached_image.save()  # sets last_updated time
    return cached_image


def sandbox_embed_html(url, html):
    soup = BeautifulSoup(html, "html.parser")
    iframe = soup.find("iframe")
    iframe_url = iframe.attrs["src"]
    scheme, netloc, path, params, query, fragment = urlparse(url)
    iframe_scheme, iframe_netloc, iframe_path, iframe_params, iframe_query, iframe_fragment = urlparse(
        iframe_url
    )

    scheme = "https"
    querydict = parse_qs(iframe_query)
    querydict.update(parse_qs(query))
    query = urlencode(querydict, doseq=1)

    # host = ".".join(iframe_netloc.split(".")[-2:])

    iframe.attrs["referrerpolicy"] = "no-referrer"
    iframe.attrs["sandbox"] = "allow-scripts allow-same-origin"
    iframe.attrs["frameborder"] = 0
    iframe.attrs["allowfullscreen"] = True

    # "accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture"
    iframe.attrs["allow"] = "fullscreen"
    # iframe.attrs["csp"] = "default-src 'self' *.{1}; img-src '*';".format(scheme, host)
    iframe.attrs["src"] = urlunparse(
        (scheme, iframe_netloc, iframe_path, params, query, fragment)
    )

    return str(soup)
