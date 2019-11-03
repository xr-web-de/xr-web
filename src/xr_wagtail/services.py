from django.db.models import F
from wagtail.core.models import PageRevision


def get_old_revisions_for_all_pages():
    revisions = (
        PageRevision.objects.filter(submitted_for_moderation=False)
        .filter(approved_go_live_at__isnull=True)
        .exclude(page__live_revision_id=F("id"))
        .filter(page__live_revision__created_at__gte=F("created_at"))
        .order_by("page__title", "-created_at")
        .select_related("page", "page__live_revision")
    )
    return revisions
