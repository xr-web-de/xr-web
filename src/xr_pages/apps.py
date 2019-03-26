from django.apps import AppConfig


class XrPagesConfig(AppConfig):
    name = "xr_pages"

    def ready(self):
        import xr_pages.signals  # noqa
