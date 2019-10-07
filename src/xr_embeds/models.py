import logging

from django.db import models


logger = logging.getLogger(__name__)


class CachedImage(models.Model):
    image = models.ImageField(upload_to="cached_images")
    last_updated = models.DateTimeField(auto_now=True)
    original_url = models.URLField(unique=True)
