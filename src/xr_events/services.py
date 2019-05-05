from xr_pages.services import get_home_page


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
        event_group_pages = EventGroupPage.objects.child_of(event_list_page).live()
    except (KeyError, AttributeError, EventGroupPage.DoesNotExist):
        return []
    return event_group_pages
