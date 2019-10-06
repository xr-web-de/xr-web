from django.contrib import messages
from django.db.models import F
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render

# Create your views here.
from django.urls import reverse
from django.utils.translation import ugettext
from wagtail.core.models import Page, PageRevision


def remove_old_revisions_for_page(request, page_id):
    page = get_object_or_404(Page, id=page_id)

    perms = page.permissions_for_user(request.user)
    if not request.user.is_superuser and not perms.can_edit():
        return HttpResponseForbidden()

    next = request.META.get("HTTP_REFERER", None)

    # get revisions for page
    revisions = (
        PageRevision.objects.filter(page_id=page.id)
        .filter(submitted_for_moderation=False)
        .filter(approved_go_live_at__isnull=True)
        .exclude(id=page.live_revision_id)
        .filter(created_at__lt=page.live_revision.created_at)
    )

    if request.POST:
        revisions.delete()

        messages.success(
            request, ugettext('Old revisions of "{}" have been deleted.'.format(page))
        )

        next = request.POST.get("next", next)

        if next:
            return redirect(next)

        return redirect(reverse("wagtailadmin_pages:revisions_index", args=[page_id]))

    else:
        return render(
            request,
            "xr_wagtail/revisions/remove_for_page_confirm.html",
            context={
                "page": page,
                "revisions": revisions,
                "next": reverse("wagtailadmin_pages:revisions_index", args=[page_id]),
            },
        )


def remove_old_revisions_for_all_pages(request):
    if not request.user.is_superuser:
        return HttpResponseForbidden()

    revisions = (
        PageRevision.objects.filter(submitted_for_moderation=False)
        .filter(approved_go_live_at__isnull=True)
        .exclude(page__live_revision_id=F("id"))
        .filter(page__live_revision__created_at__gte=F("created_at"))
        .order_by("page__title", "-created_at")
        .select_related("page", "page__live_revision")
    )

    next = request.META.get("HTTP_REFERER", None)

    if request.POST:
        revisions.delete()

        messages.success(
            request, ugettext("Old revisions of all pages have been deleted.")
        )

        next = request.POST.get("next", next)

        if next:
            return redirect(next)
        return redirect(reverse("wagtailadmin_home"))

    else:
        return render(
            request,
            "xr_wagtail/revisions/remove_for_all_pages_confirm.html",
            context={"revisions": revisions, "next": next},
        )
