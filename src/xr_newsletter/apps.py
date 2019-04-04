from django.apps import AppConfig


class XrNewsletterConfig(AppConfig):
    name = "xr_newsletter"

    def ready(self):
        import xr_newsletter.signals  # noqa
