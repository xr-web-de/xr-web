from django.contrib.staticfiles.templatetags.staticfiles import static
from django.http import JsonResponse, Http404
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext as _
from wagtail.embeds.models import Embed

from xr_pages.models import LocalGroup


def embed_html_view(request, embed_id):
    embed = get_object_or_404(Embed, id=embed_id)

    data = {"embed_html": embed.html, "success": True}

    return JsonResponse(data)


def geojson_view(request, model_slug, query_slug):
    """GeoJson export for umap"""

    if model_slug == "local_group":
        model_queryset = LocalGroup.objects.exclude(is_regional_group=True)

        if query_slug == "all":
            model_queryset = model_queryset
        elif query_slug == "active":
            model_queryset = model_queryset.active()
        elif query_slug == "in_foundation":
            model_queryset = model_queryset.in_foundation()
        elif query_slug == "idle":
            model_queryset = model_queryset.idle()
        else:
            raise Http404()
    else:
        raise Http404()

    features = []

    for obj in model_queryset:
        if not (hasattr(obj, "lnglat") and obj.lnglat and "," in obj.lnglat):
            continue

        name = obj.name

        if obj.area_description:
            name = "{} {}".format(obj.name, obj.area_description)

        description = ""

        for attr_name in ["facebook", "twitter", "youtube", "instagram", "mastodon"]:
            if hasattr(obj, attr_name) and getattr(obj, attr_name):
                description = "[[{}|{}]]".format(
                    getattr(obj, attr_name), attr_name.capitalize()
                )
                break

        if obj.full_url:
            description = "[[{}|{}]]".format(obj.full_url, _("Homepage"))

        if obj.email:
            description += "\n[[mailto:{}|{}]]".format(obj.email, obj.email)

        icon_url = request.build_absolute_uri(static("img/extinctionsymbol_48.png"))

        features.append(
            {
                "type": "Feature",
                "properties": {
                    "name": name,
                    "description": description,
                    "_umap_options": {},
                },
                "geometry": {
                    "type": "Point",
                    "coordinates": [obj.lnglat.split(",")[0], obj.lnglat.split(",")[1]],
                },
            }
        )

    data = {
        "type": "FeatureCollection",
        "features": features,
        "_umap_options": {"iconURL": icon_url},
    }

    return JsonResponse(data)
