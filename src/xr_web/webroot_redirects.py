from django.contrib.staticfiles.storage import staticfiles_storage
from django.urls import re_path
from django.views.generic import RedirectView


urlpatterns = [
    re_path(
        r"^favicon.ico$",
        RedirectView.as_view(
            url=staticfiles_storage.url("favicons/favicon.ico"), permanent=True
        ),
    ),
    re_path(
        r"^favicon.ico$",
        RedirectView.as_view(
            url=staticfiles_storage.url("browserconfig.xml"), permanent=True
        ),
    ),
    re_path(
        r"^favicon.ico$",
        RedirectView.as_view(url=staticfiles_storage.url("robots.txt"), permanent=True),
    ),
    re_path(
        r"^favicon.ico$",
        RedirectView.as_view(
            url=staticfiles_storage.url("site.webmanifest"), permanent=True
        ),
    ),
]
