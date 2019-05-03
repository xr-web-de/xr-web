from django.apps import AppConfig


class XrBlogConfig(AppConfig):
    name = "xr_blog"

    def ready(self):
        import xr_blog.signals  # noqa
