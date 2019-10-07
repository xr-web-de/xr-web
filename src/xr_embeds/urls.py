from django.urls import re_path

from xr_embeds.views import geojson_view, embed_html_view

app_name = "embeds"

urlpatterns = [
    re_path(r"^(\d+)/html/$", embed_html_view, name="embed_html"),
    re_path(
        r"^geojson/(?P<model_slug>\w+)/(?P<query_slug>\w+)/$",
        geojson_view,
        name="geojson_view",
    ),
]
