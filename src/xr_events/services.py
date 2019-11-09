import datetime

from django.utils.timezone import localdate

from xr_pages.services import (
    get_home_page,
    MODERATORS_PAGE_PERMISSIONS,
    EDITORS_PAGE_PERMISSIONS,
)

EVENT_MODERATORS_SUFFIX = "Event Moderators"
EVENT_EDITORS_SUFFIX = "Event Editors"
EVENT_AUTH_GROUP_TYPES = [EVENT_MODERATORS_SUFFIX, EVENT_EDITORS_SUFFIX]

MODERATORS_EVENT_PERMISSIONS = MODERATORS_PAGE_PERMISSIONS
EDITORS_EVENT_PERMISSIONS = EDITORS_PAGE_PERMISSIONS


def get_event_list_page(request=None):
    from .models import EventListPage

    home_page = get_home_page(request)

    try:
        event_list_page = EventListPage.objects.child_of(home_page).live().get()
    except (KeyError, AttributeError, EventListPage.DoesNotExist):
        return None
    return event_list_page


def get_event_group_pages(request=None):
    from .models import EventGroupPage

    event_list_page = get_event_list_page(request)

    try:
        event_group_pages = (
            EventGroupPage.objects.child_of(event_list_page)
            .live()
            .order_by("-group__is_regional_group", "group__name")
        )
    except (KeyError, AttributeError, EventGroupPage.DoesNotExist):
        return []

    # # arrange regional group pages at the start
    # if any([page.is_regional_group for page in event_group_pages]):
    #     regional_pages = [page for page in event_group_pages if page.is_regional_group]
    #     local_pages = [page for page in event_group_pages if not page.is_regional_group]
    #     event_group_pages = regional_pages + local_pages

    return event_group_pages


def date_range_from_days(days):
    days = int(days)

    if days > 0:
        from_date = localdate()
        to_date = localdate() + datetime.timedelta(days=days)
    elif days < 0:
        from_date = localdate() + datetime.timedelta(days=days)
        to_date = localdate()
    else:
        from_date = localdate()
        to_date = localdate() + datetime.timedelta(days=30)

    return from_date, to_date
