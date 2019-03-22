from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from wagtail.core.models import GroupPagePermission

from xr_pages.models import HomePage
from xr_pages.services import EVENT_AUTH_GROUP_TYPES


def get_or_create_or_update_auth_group_for_event_group_page(page, group_type):
    from xr_events.models import EventGroupPage

    if not isinstance(page, EventGroupPage):
        raise ValidationError("Object '%s' must be an instance of Page." % page)

    if group_type not in EVENT_AUTH_GROUP_TYPES:
        raise ValidationError("Invalid group_type '%s'." % group_type)

    homepage = HomePage.objects.ancestor_of(page).live().first()

    if page.is_regional_group:
        group_name = "%s %s" % (homepage.specific.group_name, group_type)
    elif page.local_group:
        group_name = "%s %s" % (page.local_group.specific.name, group_type)

    # first check for existing group by name
    group_qs = Group.objects.filter(name=group_name)

    if group_qs.exists():
        return group_qs.get()

    # second check for an appropriate group_page_permission
    group_page_permission_qs = GroupPagePermission.objects.filter(
        page=page, group__name__endswith=group_type
    )
    if group_page_permission_qs.exists():
        group_page_permission = group_page_permission_qs.first()
        group = group_page_permission.group
        # the name has changed so we update the existing group
        group.name = group_name
        group.save()
        return group

    # else create a new auth group
    return Group.objects.create(name=group_name)
