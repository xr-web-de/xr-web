from django.db import models


class VideoThumbnail(models.Model):
    thumbnail = models.ImageField(upload_to="video_thumbnails/")
    last_updated = models.DateTimeField(auto_now=True)
    thumbnail_url = models.URLField()
