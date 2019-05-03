from django.db.models.signals import post_save

from xr_blog.models import BlogListPage
from xr_pages.services import (
    get_auth_groups,
    set_auth_groups_page_permissions,
    PAGE_AUTH_GROUP_TYPES,
    MODERATORS_PAGE_PERMISSIONS,
    EDITORS_PAGE_PERMISSIONS,
)


# FormPages


def create_blog_page_permissions(sender, instance, created=False, **kwargs):
    if created:
        if instance.specific.group.is_regional_group:
            auth_groups = get_auth_groups(
                local_group=instance.group, auth_group_types=PAGE_AUTH_GROUP_TYPES
            )
            set_auth_groups_page_permissions(
                auth_groups,
                instance,
                MODERATORS_PAGE_PERMISSIONS,
                EDITORS_PAGE_PERMISSIONS,
            )


post_save.connect(
    create_blog_page_permissions,
    sender=BlogListPage,
    dispatch_uid="create_blog_page_permissions_once",
)
