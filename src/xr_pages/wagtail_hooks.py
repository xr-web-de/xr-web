from django.utils.translation import ugettext as _
from wagtail.admin.utils import permission_denied
from wagtail.contrib.modeladmin.helpers import PermissionHelper
from wagtail.contrib.modeladmin.options import ModelAdmin, modeladmin_register
from wagtail.core import hooks

from xr_pages.services import get_auth_groups, PAGE_MODERATORS_SUFFIX
from .models import LocalGroupPage, LocalGroup


class LocalGroupPermissionHelper(PermissionHelper):
    def user_has_any_permissions(self, user):
        """
        Give additional change permission, if the user has
        permissions to publish events or group_pages for a local group
        """
        for auth_type in self.get_moderators_auth_group_types():
            if any([group.name.endswith(auth_type) for group in user.groups.all()]):
                return True
        return super().user_has_any_permissions(user)

    def user_can_edit_obj(self, user, obj):
        """
        Return a boolean to indicate whether `user` is permitted to 'change'
        a specific `local group` instance.
        """
        moderator_groups = get_auth_groups(obj, self.get_moderators_auth_group_types())
        if set(user.groups.all()).intersection(moderator_groups):
            return True
        return super().user_can_edit_obj(user, obj)

    def get_moderators_auth_group_types(self):
        from xr_events.services import EVENT_MODERATORS_SUFFIX

        return [PAGE_MODERATORS_SUFFIX, EVENT_MODERATORS_SUFFIX]


class LocalGroupAdmin(ModelAdmin):
    model = LocalGroup
    permission_helper_class = LocalGroupPermissionHelper
    menu_label = _("Local groups")
    menu_icon = "group"
    menu_order = 200
    add_to_settings_menu = False
    list_display = (
        "name",
        "email",
        "url",
        "state",
        "location",
        "status",
        "founding_date",
    )
    list_filter = ("status", "founding_date", "state")
    search_fields = ("name", "email", "area_description", "location")
    ordering = ("name",)


modeladmin_register(LocalGroupAdmin)


@hooks.register("before_delete_page")
@hooks.register("before_copy_page")
def protect_base_and_local_group_pages(request, page):
    if request.user.is_superuser:
        return

    if isinstance(page.specific, LocalGroupPage):
        if page.group.is_regional_group:
            return permission_denied(request)
