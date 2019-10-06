"""
Django settings for xr_web project.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.1/ref/settings/
"""

import re
import os
import django


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
# this evaluates to path/to/project/src/
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.1/howto/deployment/checklist/

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False
TESTING = False

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    # Django
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Django 3rd Party
    "webpack_loader",
    "django_extensions",
    "widget_tweaks",
    # Wagtail
    "wagtail.contrib.forms",
    "wagtail.contrib.redirects",
    "wagtail.embeds",
    "wagtail.sites",
    "wagtail.users",
    "wagtail.snippets",
    "wagtail.documents",
    "wagtail.images",
    "wagtail.search",
    "wagtail.admin",
    "wagtail.core",
    "modelcluster",
    "taggit",
    "wagtail.contrib.modeladmin",
    # Wagtail 3rd Party
    "wagtailmenus",
    "condensedinlinepanel",
    # Project
    "xr_wagtail",
    "xr_pages",
    "xr_events",
    "xr_newsletter",
    "xr_blog",
]

MIDDLEWARE = [
    # Django
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    # Wagtail
    "wagtail.core.middleware.SiteMiddleware",
    "wagtail.contrib.redirects.middleware.RedirectMiddleware",
]

ROOT_URLCONF = "xr_web.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            os.path.join(BASE_DIR, "xr_web", "templates"),
            os.path.join(BASE_DIR, "xr_wagtail", "templates"),
            os.path.join(django.__path__[0], "forms", "templates"),
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "wagtailmenus.context_processors.wagtailmenus",
            ]
        },
    }
]

FORM_RENDERER = "django.forms.renderers.TemplatesSetting"

WSGI_APPLICATION = "xr_web.wsgi.application"

# Session
SESSION_COOKIE_NAME = "xr_web_session"

# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.path.join(os.path.dirname(BASE_DIR), "db.sqlite3"),
    }
}


# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]


# Internationalization
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = "de-de"

TIME_ZONE = "Europe/Berlin"

USE_I18N = True

USE_L10N = True

USE_TZ = True

LOCALE_PATHS = [os.path.join(BASE_DIR, "locale")]

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/

STATIC_URL = "/static/"

STATIC_ROOT = os.path.join(os.path.dirname(BASE_DIR), "static")
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "xr_web", "static"),
    os.path.join(os.path.dirname(BASE_DIR), "webpack", "static"),
]

MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(os.path.dirname(BASE_DIR), "media")


WEBPACK_LOADER = {
    "DEFAULT": {
        "BUNDLE_DIR_NAME": "bundles/",
        "STATS_FILE": os.path.join(
            os.path.dirname(BASE_DIR), "webpack", "webpack-stats-production.json"
        ),
    }
}


# Wagtail
# ------------
WAGTAIL_SITE_NAME = "XR de"

# Wagtailmenus
WAGTAILMENUS_DEFAULT_MAIN_MENU_TEMPLATE = "xr_pages/menus/main_menu.html"
WAGTAILMENUS_DEFAULT_FLAT_MENU_TEMPLATE = "xr_pages/menus/flat_menu.html"
WAGTAILMENUS_DEFAULT_CHILDREN_MENU_TEMPLATE = (
    "xr_pages/menus/local_group_level_3_menu.html"
)

WAGTAILMENUS_MAIN_MENUS_MODELADMIN_CLASS = "xr_wagtail.wagtail_hooks.XrMainMenuAdmin"


# Local Group Settings
GERMANY_STATE_CHOICES = (
    ("BW", "Baden-Württemberg"),
    ("BY", "Bayern"),
    ("BE", "Berlin"),
    ("BB", "Brandenburg"),
    ("HB", "Bremen"),
    ("HH", "Hamburg"),
    ("HE", "Hessen"),
    ("MV", "Mecklenburg-Vorpommern"),
    ("NI", "Niedersachsen"),
    ("NW", "Nordrhein-Westfalen"),
    ("RP", "Rheinland-Pfalz"),
    ("SL", "Saarland"),
    ("SN", "Sachsen"),
    ("ST", "Sachsen-Anhalt"),
    ("SH", "Schleswig-Holstein"),
    ("TH", "Thüringen"),
)
LOCAL_GROUP_STATE_CHOICES = GERMANY_STATE_CHOICES

UMAP_URLS = []

MAUTIC_DEFAULT_FORM_ID = None


# Logging
# ------------
def filter_404(record):
    if getattr(record, "status_code", None) == 404 and re.match(
        r"^Not Found: ", record.msg
    ):
        return False
    else:
        return True


LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "application_file": {
            "level": "DEBUG",
            "class": "logging.FileHandler",
            "filename": os.path.join(
                os.path.dirname(os.path.dirname(BASE_DIR)), "log", "application.log"
            ),
        },
        "template_file": {
            "level": "DEBUG",
            "class": "logging.FileHandler",
            "filename": os.path.join(
                os.path.dirname(os.path.dirname(BASE_DIR)), "log", "template.log"
            ),
        },
        "debug_file": {
            "level": "DEBUG",
            "class": "logging.FileHandler",
            "filename": os.path.join(
                os.path.dirname(os.path.dirname(BASE_DIR)), "log", "application.log"
            ),
        },
        "error_file": {
            "level": "ERROR",
            "class": "logging.FileHandler",
            "filename": os.path.join(
                os.path.dirname(os.path.dirname(BASE_DIR)), "log", "error.log"
            ),
        },
        "mail_admins": {
            "level": "ERROR",
            "class": "django.utils.log.AdminEmailHandler",
        },
    },
    "loggers": {
        "django.request": {"filters": ["filter_404"]},
        "django.template": {"handlers": ["template_file"], "level": "INFO"},
        "": {"handlers": ["mail_admins", "error_file"], "level": "ERROR"},
        "app": {"handlers": ["application_file"], "level": "DEBUG"},
    },
    "filters": {
        "filter_404": {"()": "django.utils.log.CallbackFilter", "callback": filter_404}
    },
    "formatters": {
        "advanced": {"format": "%(levelname)s %(asctime)s %(module)s %(message)s"}
    },
}
