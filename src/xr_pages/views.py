from django.http import JsonResponse

from .models import LocalGroup


def umap_marker(request):
    """LocalGroup GeoJson export for umap."""
    features = []

    local_group_qs = LocalGroup.objects.exclude(is_regional_group=True)
    if "in_foundation" in request.GET:
        local_group_qs = local_group_qs.in_foundation()
    else:
        local_group_qs = local_group_qs.active()

    for group in local_group_qs:
        if not group.lnglat or "," not in group.lnglat:
            continue

        features.append(
            {
                "type": "Feature",
                "properties": {
                    "name": group.name,
                    "description": "[[{url}]]".format(url=group.full_url),
                },
                "geometry": {
                    "type": "Point",
                    "coordinates": [
                        group.lnglat.split(",")[0],
                        group.lnglat.split(",")[1],
                    ],
                },
            }
        )

    data = {"type": "FeatureCollection", "features": features}

    return JsonResponse(data)
