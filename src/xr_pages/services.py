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

PAGE_MODERATORS_SUFFIX = "Page Moderators"
PAGE_EDITORS_SUFFIX = "Page Editors"
EVENT_MODERATORS_SUFFIX = "Event Moderators"
EVENT_EDITORS_SUFFIX = "Event Editors"

COMMON_COLLECTION_NAME = "Common"

PAGE_AUTH_GROUP_TYPES = [PAGE_MODERATORS_SUFFIX, PAGE_EDITORS_SUFFIX]
EVENT_AUTH_GROUP_TYPES = [EVENT_MODERATORS_SUFFIX, EVENT_EDITORS_SUFFIX]
AUTH_GROUP_TYPES = PAGE_AUTH_GROUP_TYPES + EVENT_AUTH_GROUP_TYPES
AVAILABLE_PAGE_PERMISSION_TYPES = [key for key, _ in PAGE_PERMISSION_TYPE_CHOICES]

IMAGE_PERMISSION_CODENAMES = ["add_image", "change_image"]  # change includes delete
DOCUMENT_PERMISSION_CODENAMES = ["add_document", "change_document"]
AVAILABLE_COLLECTION_PERMISSION_TYPES = (
    IMAGE_PERMISSION_CODENAMES + DOCUMENT_PERMISSION_CODENAMES
)

MODERATORS_PAGE_PERMISSIONS = ["add", "edit", "publish"]
MODERATORS_IMAGE_PERMISSIONS = IMAGE_PERMISSION_CODENAMES
MODERATORS_DOCUMENT_PERMISSIONS = DOCUMENT_PERMISSION_CODENAMES
MODERATORS_COLLECTION_PERMISSIONS = AVAILABLE_COLLECTION_PERMISSION_TYPES

EDITORS_PAGE_PERMISSIONS = ["add", "edit"]
EDITORS_IMAGE_PERMISSIONS = IMAGE_PERMISSION_CODENAMES
EDITORS_DOCUMENT_PERMISSIONS = DOCUMENT_PERMISSION_CODENAMES
EDITORS_COLLECTION_PERMISSIONS = AVAILABLE_COLLECTION_PERMISSION_TYPES


def get_auth_group_name(page_group_name, group_type):
    return "%s %s" % (page_group_name, group_type)


def get_or_create_or_update_page_auth_group_for_local_group_page(page, group_type):
    from xr_pages.models import LocalGroupPage

    if not isinstance(page, LocalGroupPage):
        raise ValidationError("Object '%s' must be an instance of Page." % page)

    if group_type not in PAGE_AUTH_GROUP_TYPES:
        raise ValidationError("Invalid group_type '%s'." % group_type)

    group_name = get_auth_group_name(page.name, group_type)

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
    if permission_type not in AVAILABLE_PAGE_PERMISSION_TYPES:
        raise ValidationError("Invalid permission_type '%s'." % permission_type)

    group_page_permission, created = GroupPagePermission.objects.get_or_create(
        group=group, page=page, permission_type=permission_type
    )
    return group_page_permission


def get_collection_permission(permission_type):
    if permission_type not in AVAILABLE_COLLECTION_PERMISSION_TYPES:
        raise ValidationError(
            "Invalid collection_permission_type '%s'." % permission_type
        )

    if permission_type.endswith("document"):
        content_type = ContentType.objects.get(
            model="document", app_label="wagtaildocs"
        )
    elif permission_type.endswith("image"):
        content_type = ContentType.objects.get(model="image", app_label="wagtailimages")
    else:
        raise ValidationError(
            "Invalid collection_permission_type '%s'." % permission_type
        )

    permission = Permission.objects.get(
        content_type=content_type, codename=permission_type
    )
    return permission


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
