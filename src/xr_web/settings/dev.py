from .base import *  # noqa
import os

SECRET_KEY = "not secret at all"

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"


ALLOWED_HOSTS = ["0.0.0.0", "localhost", "127.0.0.1"]
DEBUG = True
for template_engine in TEMPLATES:  # noqa
    template_engine["OPTIONS"]["debug"] = DEBUG


INSTALLED_APPS += ["wagtail.contrib.styleguide"]  # noqa


WEBPACK_LOADER = {
    "DEFAULT": {
        "BUNDLE_DIR_NAME": "bundles/",
        "STATS_FILE": os.path.join(  # noqa
            os.path.dirname(BASE_DIR), "webpack", "webpack-stats.json"  # noqa
        ),
    }
}


# log everything to console
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"console": {"level": "DEBUG", "class": "logging.StreamHandler"}},
    "filters": {
        "filter_404": {
            "()": "django.utils.log.CallbackFilter",
            "callback": filter_404,  # noqa
        }
    },
    "loggers": {
        "django.request": {"filters": ["filter_404"]},
        "": {"handlers": ["console"], "level": "DEBUG"},
    },
}


SENDY_HOST_URL = "https://sendy.testhost"
SENDY_API_KEY = "NotSecretAtAll"

MAUTIC_SUBMIT_URL = "https://mautic.extinctionrebellion.de"
MAUTIC_DEFAULT_FORM_ID = 3
