from django.db.models.signals import pre_delete, ModelSignal, post_save
from django.dispatch import receiver

from .services import (
    delete_auth_groups,
    create_auth_groups,
    update_auth_group_names,
    set_auth_groups_collection_permissions,
    set_auth_groups_page_permissions,
    PAGE_AUTH_GROUP_TYPES,
    MODERATORS_PAGE_PERMISSIONS,
    EDITORS_PAGE_PERMISSIONS,
    COMMON_COLLECTION_NAME,
    MODERATORS_COLLECTION_PERMISSIONS,
    EDITORS_COLLECTION_PERMISSIONS,
    get_auth_groups,
)
from .models import LocalGroup, LocalGroupPage, HomeSubPage

# Custom Signals

local_group_create = ModelSignal(providing_args=["instance"])
local_group_name_change = ModelSignal(
    providing_args=["instance", "old_name", "new_name"]
)


# LocalGroup


@receiver(
    local_group_name_change,
    sender=LocalGroup,
    dispatch_uid="update_pages_auth_group_names_once",
)
def update_pages_auth_group_names(sender, instance=None, created=False, **kwargs):
    if not created and instance.old_name != instance.name:
        update_auth_group_names(
            local_group=instance, auth_group_types=PAGE_AUTH_GROUP_TYPES
        )


# LocalGroupPage


@receiver(
    post_save,
    sender=LocalGroupPage,
    dispatch_uid="create_local_group_page_auth_groups_once",
)
def create_local_group_page_auth_groups(sender, instance, created=False, **kwargs):
    if created:
        auth_groups = create_auth_groups(
            local_group=instance.group, auth_group_types=PAGE_AUTH_GROUP_TYPES
        )
        set_auth_groups_collection_permissions(
            auth_groups,
            collection_name=COMMON_COLLECTION_NAME,
            moderators_permissions=MODERATORS_COLLECTION_PERMISSIONS,
            editors_permissions=EDITORS_COLLECTION_PERMISSIONS,
        )
        set_auth_groups_page_permissions(
            auth_groups, instance, MODERATORS_PAGE_PERMISSIONS, EDITORS_PAGE_PERMISSIONS
        )


@receiver(
    pre_delete,
    sender=LocalGroupPage,
    dispatch_uid="delete_local_group_page_auth_groups_once",
)
def delete_local_group_page_auth_groups(sender, instance, **kwargs):
    delete_auth_groups(
        local_group=instance.group, auth_group_types=PAGE_AUTH_GROUP_TYPES
    )


# HomeSubPage


@receiver(
    post_save, sender=HomeSubPage, dispatch_uid="create_home_sub_page_permissions_once"
)
def create_home_sub_page_permissions(sender, instance, created=False, **kwargs):
    if created:
        regional_group = LocalGroup.objects.get(is_regional_group=True)

        auth_groups = get_auth_groups(
            local_group=regional_group, auth_group_types=PAGE_AUTH_GROUP_TYPES
        )
        set_auth_groups_page_permissions(
            auth_groups, instance, MODERATORS_PAGE_PERMISSIONS, EDITORS_PAGE_PERMISSIONS
        )
