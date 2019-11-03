"""xr_web URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf import settings
from django.contrib import admin
from django.urls import include, path, re_path
from wagtail.admin import urls as wagtailadmin_urls
from wagtail.core import urls as wagtail_urls
from wagtail.documents import urls as wagtaildocs_urls

from xr_wagtail.views import (
    remove_old_revisions_for_page,
    remove_old_revisions_for_all_pages,
)
from xr_embeds import urls as xr_embeds_urls

from . import webroot_redirects

urlpatterns = [
    re_path(
        r"^admin/pages/(\d+)/revisions/remove_old/$",
        remove_old_revisions_for_page,
        name="remove_old_revisions_for_page",
    ),
    re_path(
        r"^admin/remove_old_revisions/$",
        remove_old_revisions_for_all_pages,
        name="remove_old_revisions_for_all_pages",
    ),
    re_path(r"^embeds/", include(xr_embeds_urls)),
    re_path(r"^django-admin/", admin.site.urls),
    re_path(r"^documents/", include(wagtaildocs_urls)),
    re_path(r"^admin/", include(wagtailadmin_urls)),
    re_path(r"", include(wagtail_urls)),
]


if settings.DEBUG or settings.TESTING:
    from django.conf.urls.static import static
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns
    from django.views.defaults import server_error, page_not_found
    from django.http import Http404

    # Serve static and media files from development server
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

    # Serve error pages
    urlpatterns = [
        path("500/", server_error),
        path("404/", page_not_found, {"exception": Http404()}),
    ] + urlpatterns

    # Serve static webroot files
    urlpatterns = webroot_redirects.urlpatterns + urlpatterns
