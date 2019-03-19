from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from wagtail.core.models import (
    PAGE_PERMISSION_TYPE_CHOICES,
    GroupPagePermission,
    Page,
    GroupCollectionPermission,
    Collection,
)

PAGE_AUTH_GROUP_TYPES = ["Page Moderators", "Page Editors"]
EVENT_AUTH_GROUP_TYPES = ["Event Moderators", "Event Editors"]
AUTH_GROUP_TYPES = PAGE_AUTH_GROUP_TYPES + EVENT_AUTH_GROUP_TYPES
PAGE_PERMISSION_TYPES = [key for key, _ in PAGE_PERMISSION_TYPE_CHOICES]
IMAGE_PERMISSION_CODENAMES = ["add_image", "change_image", "delete_image", "view_image"]
DOCUMENT_PERMISSION_CODENAMES = [
    "add_document",
    "change_document",
    "delete_document",
    "view_document",
]


def get_or_create_or_update_page_auth_group_for_local_group_page(page, group_type):
    from xr_pages.models import LocalGroupPage

    if not isinstance(page, LocalGroupPage):
        raise ValidationError("Object '%s' must be an instance of Page." % page)

    if group_type not in PAGE_AUTH_GROUP_TYPES:
        raise ValidationError("Invalid group_type '%s'." % group_type)

    group_name = "%s %s" % (page.name, group_type)

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


def get_or_create_or_update_event_auth_group_for_local_group_page(page, group_type):
    from xr_pages.models import LocalGroupPage

    if not isinstance(page, LocalGroupPage):
        raise ValidationError("Object '%s' must be an instance of Page." % page)

    if group_type not in EVENT_AUTH_GROUP_TYPES:
        raise ValidationError("Invalid group_type '%s'." % group_type)

    group_name = "%s %s" % (page.name, group_type)

    # first check for existing group by name
    group_qs = Group.objects.filter(name=group_name)

    if group_qs.exists():
        return group_qs.get()

    # second check for an appropriate group_page_permission
    if page.event_group:
        group_page_permission_qs = GroupPagePermission.objects.filter(
            page=page.event_group, group__name__endswith=group_type
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


def get_or_create_or_update_page_auth_group_for_home_page(page, group_type):
    from xr_pages.models import HomePage, HomeSubPage

    if not isinstance(page, HomePage):
        raise ValidationError("Object '%s' must be an instance of Page." % page)

    if group_type not in PAGE_AUTH_GROUP_TYPES:
        raise ValidationError("Invalid group_type '%s'." % group_type)

    group_name = "%s %s" % (page.group_name, group_type)

    # first check for existing group by name
    group_qs = Group.objects.filter(name=group_name)

    if group_qs.exists():
        return group_qs.get()

    # second look for a subpage
    subpage_qs = HomeSubPage.objects.all()

    if subpage_qs.exists():
        subpage = subpage_qs.first()
        # and look for an appropriate group_page_permission
        group_page_permission_qs = GroupPagePermission.objects.filter(
            page=subpage, group__name__endswith=group_type
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


def get_or_create_or_update_event_auth_group_for_home_page(page, group_type):
    from xr_pages.models import HomePage
    from xr_events.models import EventGroupPage

    if not isinstance(page, HomePage):
        raise ValidationError("Object '%s' must be an instance of Page." % page)

    if group_type not in EVENT_AUTH_GROUP_TYPES:
        raise ValidationError("Invalid group_type '%s'." % group_type)

    group_name = "%s %s" % (page.group_name, group_type)

    # first check for existing group by name
    group_qs = Group.objects.filter(name=group_name)

    if group_qs.exists():
        return group_qs.get()

    # second look for an event_group_page
    event_group_page_qs = EventGroupPage.objects.filter(is_regional_group=True)

    if event_group_page_qs.exists():
        event_group_page = event_group_page_qs.first()
        # and look for an appropriate group_page_permission
        group_page_permission_qs = GroupPagePermission.objects.filter(
            page=event_group_page, group__name__endswith=group_type
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


def add_group_page_permission(group, page, permission_type):
    if not isinstance(group, Group):
        raise ValidationError("Object '%s' must be an instance of Group." % group)
    if not isinstance(page, Page):
        raise ValidationError("Object '%s' must be an instance of Page." % page)
    if permission_type not in PAGE_PERMISSION_TYPES:
        raise ValidationError("Invalid permission_type '%s'." % permission_type)

    group_page_permission, created = GroupPagePermission.objects.get_or_create(
        group=group, page=page, permission_type=permission_type
    )
    return group_page_permission


def get_document_permission(permission_codename):
    if permission_codename not in DOCUMENT_PERMISSION_CODENAMES:
        raise ValidationError("Invalid permission_codename '%s'." % permission_codename)

    document_content_type = ContentType.objects.get(
        model="document", app_label="wagtaildocs"
    )
    document_permission = Permission.objects.get(
        content_type=document_content_type, codename=permission_codename
    )
    return document_permission


def get_image_permission(permission_codename):
    if permission_codename not in IMAGE_PERMISSION_CODENAMES:
        raise ValidationError("Invalid permission_codename '%s'." % permission_codename)

    image_content_type = ContentType.objects.get(
        model="image", app_label="wagtailimages"
    )
    image_permission = Permission.objects.get(
        content_type=image_content_type, codename=permission_codename
    )
    return image_permission


def add_group_collection_permission(group, collection, permission):
    if not isinstance(group, Group):
        raise ValidationError("Object '%s' must be an instance of Group." % group)
    if not isinstance(collection, Collection):
        raise ValidationError(
            "Object '%s' must be an instance of Collection." % collection
        )
    if not isinstance(permission, Permission):
        raise ValidationError(
            "Object '%s' must be an instance of Permission." % permission
        )

    group_collection_permission, created = GroupCollectionPermission.objects.get_or_create(
        group=group, collection=collection, permission=permission
    )
    return group_collection_permission
