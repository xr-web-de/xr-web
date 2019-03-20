from .base import *  # noqa

SECRET_KEY = "not secret at all"

TESTING = True

USE_XVFB = False

SKIP_SELENIUM = True

WEBPACK_LOADER = {
    "DEFAULT": {
        "BUNDLE_DIR_NAME": "bundles/",
        "STATS_FILE": os.path.join(  # noqa
            os.path.dirname(BASE_DIR), "webpack", "webpack-stats.json"  # noqa
        ),
    }
}


# DATABASE MIGRATIONS
# Disable migrations when running tests
class DisableMigrations(object):
    def __contains__(self, item):
        return True

    def __getitem__(self, item):
        return None


# MIGRATION_MODULES = DisableMigrations()
# END DATABASE MIGRATIONS


# DYNAMIC FIXTURES
# Throw errors when using invalid args for G/N
DDF_VALIDATE_ARGS = True
DDF_FILL_NULLABLE_FIELDS = False
# END DYNAMIC FIXTURES

for TEMPLATE in TEMPLATES:  # noqa
    TEMPLATE.setdefault("OPTIONS", {})["debug"] = True

# log everything to console
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"console": {"class": "logging.StreamHandler"}},
    "root": {"handlers": ["console"], "level": "WARNING"},
}

CACHES = {"default": {"BACKEND": "django.core.cache.backends.dummy.DummyCache"}}

PASSWORD_HASHERS = ("django.contrib.auth.hashers.MD5PasswordHasher",)
