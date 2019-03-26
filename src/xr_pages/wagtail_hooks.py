from django.utils.translation import ugettext as _
from wagtail.admin.utils import permission_denied
from wagtail.contrib.modeladmin.options import ModelAdmin, modeladmin_register
from wagtail.core import hooks

from .models import LocalGroupListPage, LocalGroupPage, HomePage, LocalGroup


class LocalGroupAdmin(ModelAdmin):
    model = LocalGroup
    menu_label = _("Groups")
    menu_icon = "group"
    menu_order = 200
    add_to_settings_menu = False
    list_display = ("name", "email", "url", "location")
    # list_filter = ()
    search_fields = ("name", "email", "url", "location")


modeladmin_register(LocalGroupAdmin)


@hooks.register("construct_explorer_page_queryset")
def filter_local_group_pages(parent_page, pages, request):
    if request.user.is_superuser:
        return pages

    # Filter local_group_pages (don't list regional_group_pages)
    if issubclass(type(parent_page.specific), LocalGroupListPage):
        pages = LocalGroupPage.objects.child_of(parent_page).specific()
        pages = pages.filter(is_regional_group=False)

    return pages


@hooks.register("before_delete_page")
@hooks.register("before_copy_page")
def protect_base_and_local_group_pages(request, page):
    if request.user.is_superuser:
        return

    if isinstance(page.specific, LocalGroupPage):
        if page.is_regional_group:
            return permission_denied(request)
