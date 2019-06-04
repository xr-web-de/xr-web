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


def get_event_group_pages(request=None, only_with_active_events=False):
    from .models import EventGroupPage

    event_list_page = get_event_list_page(request)

    try:
        event_group_pages = (
            EventGroupPage.objects.child_of(event_list_page)
            .live()
            .order_by("group__name")
        )
    except (KeyError, AttributeError, EventGroupPage.DoesNotExist):
        return []

    # filter out pages with no active events
    if only_with_active_events:
        event_group_pages = [page for page in event_group_pages if page.upcoming_events]

    # arrange regional group pages at the start
    if any([page.is_regional_group for page in event_group_pages]):
        regional_pages = [page for page in event_group_pages if page.is_regional_group]
        local_pages = [page for page in event_group_pages if not page.is_regional_group]
        event_group_pages = regional_pages + local_pages

    return event_group_pages
