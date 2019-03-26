from django.apps import AppConfig


class XrEventsConfig(AppConfig):
    name = "xr_events"

    def ready(self):
        import xr_events.signals  # noqa
