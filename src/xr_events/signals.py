from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver

from xr_events.models import EventGroupPage
from xr_events.services import (
    EVENT_AUTH_GROUP_TYPES,
    MODERATORS_EVENT_PERMISSIONS,
    EDITORS_EVENT_PERMISSIONS,
)
from xr_pages.models import LocalGroup
from xr_pages.services import (
    update_auth_group_names,
    create_auth_groups,
    set_auth_groups_collection_permissions,
    COMMON_COLLECTION_NAME,
    MODERATORS_COLLECTION_PERMISSIONS,
    EDITORS_COLLECTION_PERMISSIONS,
    set_auth_groups_page_permissions,
    delete_auth_groups,
    set_auth_groups_wagtailadmin_access,
)
from xr_pages.signals import local_group_name_change


# LocalGroup


@receiver(
    local_group_name_change,
    sender=LocalGroup,
    dispatch_uid="update_events_auth_group_names_once",
)
def update_events_auth_group_names(sender, instance=None, **kwargs):
    update_auth_group_names(
        local_group=instance, auth_group_types=EVENT_AUTH_GROUP_TYPES
    )


# EventGroupPage


@receiver(
    post_save,
    sender=EventGroupPage,
    dispatch_uid="create_event_group_page_auth_groups_once",
)
def create_event_group_page_auth_groups(sender, instance, created=False, **kwargs):
    if created:
        auth_groups = create_auth_groups(
            local_group=instance.group, auth_group_types=EVENT_AUTH_GROUP_TYPES
        )
        set_auth_groups_wagtailadmin_access(auth_groups)
        set_auth_groups_collection_permissions(
            auth_groups,
            collection_name=COMMON_COLLECTION_NAME,
            moderators_permissions=MODERATORS_COLLECTION_PERMISSIONS,
            editors_permissions=EDITORS_COLLECTION_PERMISSIONS,
        )
        set_auth_groups_page_permissions(
            auth_groups,
            instance,
            MODERATORS_EVENT_PERMISSIONS,
            EDITORS_EVENT_PERMISSIONS,
        )


@receiver(
    pre_delete,
    sender=EventGroupPage,
    dispatch_uid="delete_event_group_page_auth_groups_once",
)
def delete_event_group_page_auth_groups(sender, instance, **kwargs):
    delete_auth_groups(
        local_group=instance.group, auth_group_types=EVENT_AUTH_GROUP_TYPES
    )
