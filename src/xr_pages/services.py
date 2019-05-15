from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from wagtail.core.models import (
    PAGE_PERMISSION_TYPE_CHOICES,
    GroupPagePermission,
    Page,
    GroupCollectionPermission,
    Collection,
    Site,
)


# Pages

PAGE_MODERATORS_SUFFIX = "Page Moderators"
PAGE_EDITORS_SUFFIX = "Page Editors"

PAGE_AUTH_GROUP_TYPES = [PAGE_MODERATORS_SUFFIX, PAGE_EDITORS_SUFFIX]

AVAILABLE_PAGE_PERMISSION_TYPES = [key for key, _ in PAGE_PERMISSION_TYPE_CHOICES]
MODERATORS_PAGE_PERMISSIONS = ["add", "edit", "publish"]
EDITORS_PAGE_PERMISSIONS = ["add", "edit"]


# Collections

COMMON_COLLECTION_NAME = "Common"

IMAGE_PERMISSION_CODENAMES = ["add_image", "change_image"]  # change includes delete
DOCUMENT_PERMISSION_CODENAMES = ["add_document", "change_document"]
AVAILABLE_COLLECTION_PERMISSION_TYPES = (
    IMAGE_PERMISSION_CODENAMES + DOCUMENT_PERMISSION_CODENAMES
)

MODERATORS_COLLECTION_PERMISSIONS = AVAILABLE_COLLECTION_PERMISSION_TYPES
EDITORS_COLLECTION_PERMISSIONS = AVAILABLE_COLLECTION_PERMISSION_TYPES


def get_auth_group_name(page_group_name, group_type):
    return "%s %s" % (page_group_name, group_type)


def create_auth_groups(local_group=None, auth_group_types=None):
    from xr_pages.models import LocalGroup

    if not isinstance(local_group, LocalGroup):
        raise ValueError(
            "Object '%s' must be an instance of xr_pages.LocalGroup." % local_group
        )

    if auth_group_types is None:
        auth_group_types = []

    auth_groups = []
    for group_type in auth_group_types:
        group_name = get_auth_group_name(local_group.name, group_type)
        group, created = Group.objects.get_or_create(name=group_name)
        auth_groups.append(group)
    return auth_groups


def get_auth_groups(local_group=None, auth_group_types=None):
    from xr_pages.models import LocalGroup

    if not isinstance(local_group, LocalGroup):
        raise ValueError(
            "Object '%s' must be an instance of xr_pages.LocalGroup." % local_group
        )

    if auth_group_types is None:
        auth_group_types = []

    auth_groups = []
    for group_type in auth_group_types:
        group_name = get_auth_group_name(local_group.name, group_type)
        group = Group.objects.get(name=group_name)
        auth_groups.append(group)
    return auth_groups


def set_auth_groups_page_permissions(
    auth_groups, page, moderators_permissions=None, editors_permissions=None
):
    if not isinstance(page, Page):
        raise ValidationError("Object '%s' must be an instance of Page." % page)

    for auth_group in auth_groups:
        if not isinstance(auth_group, Group):
            raise ValidationError(
                "Object '%s' must be an instance of Group." % auth_group
            )

        if auth_group.name.endswith("Moderators"):
            permission_types = moderators_permissions
        elif auth_group.name.endswith("Editors"):
            permission_types = editors_permissions
        else:
            raise ValidationError(
                'Group.name must end with "Moderators" or "Editors". Got "%s".'
                % auth_group.name
            )

        for permission_type in permission_types:
            add_group_page_permission(auth_group, page, permission_type)


def set_auth_groups_collection_permissions(
    auth_groups,
    collection_name=None,
    moderators_permissions=None,
    editors_permissions=None,
):
    if collection_name is None:
        collection_name = COMMON_COLLECTION_NAME
    collection = Collection.objects.get(name=collection_name)

    for auth_group in auth_groups:
        if not isinstance(auth_group, Group):
            raise ValidationError(
                "Object '%s' must be an instance of Group." % auth_group
            )

        if auth_group.name.endswith("Moderators"):
            permission_types = moderators_permissions
        elif auth_group.name.endswith("Editors"):
            permission_types = editors_permissions
        else:
            raise ValidationError(
                'Group.name must end with "Moderators" or "Editors". Got "%s".'
                % auth_group.name
            )

        for codename in permission_types:
            add_group_collection_permission(
                auth_group, collection, get_collection_permission(codename)
            )


def update_auth_group_names(local_group=None, auth_group_types=None):
    from xr_pages.models import LocalGroup

    if not isinstance(local_group, LocalGroup):
        raise ValueError(
            "local_group must be an instance of xr_pages.LocalGroup. got '%s'"
            % local_group
        )

    if auth_group_types is None:
        auth_group_types = []

    auth_groups = []
    for group_type in auth_group_types:
        old_group_name = get_auth_group_name(local_group.old_name, group_type)
        new_group_name = get_auth_group_name(local_group.name, group_type)

        if not Group.objects.filter(name=old_group_name).exists():
            continue

        group = Group.objects.get(name=old_group_name)
        group.name = new_group_name
        group.save()

        auth_groups.append(group)

    return auth_groups


def delete_auth_groups(local_group=None, auth_group_types=None):
    from xr_pages.models import LocalGroup

    if not isinstance(local_group, LocalGroup):
        raise ValueError(
            "Object '%s' must be an instance of xr_pages.LocalGroup." % local_group
        )

    if auth_group_types is None:
        auth_group_types = []

    for group_type in auth_group_types:
        group_name = get_auth_group_name(local_group.name, group_type)
        Group.objects.get(name=group_name).delete()
    return True


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


def get_site(request=None):
    try:
        site = request.site
    except AttributeError:
        site = Site.objects.all().get(is_default_site=True)
    return site


def get_home_page(request=None):
    site = get_site(request=request)
    return site.root_page.specific


def get_local_group_list_page(request=None):
    from .models import LocalGroupListPage

    home_page = get_home_page(request)
    try:
        local_group_list_page = (
            LocalGroupListPage.objects.child_of(home_page).live().get()
        )
    except (KeyError, AttributeError, LocalGroupListPage.DoesNotExist):
        return None
    return local_group_list_page


def get_local_groups(request=None):
    from .models import LocalGroup

    site = get_site(request)
    return (
        LocalGroup.objects.all()
        .filter(site=site, is_regional_group=False)
        .order_by("name")
    )
