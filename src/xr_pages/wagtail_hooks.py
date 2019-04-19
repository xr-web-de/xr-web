from django.templatetags.static import static
from django.utils.html import format_html
from django.utils.translation import ugettext as _
from wagtail.admin.utils import permission_denied
from wagtail.contrib.modeladmin.options import ModelAdmin, modeladmin_register
from wagtail.core import hooks
from wagtailmenus.modeladmin import MainMenuAdmin
from wagtailmenus.views import MainMenuEditView

from .models import LocalGroupListPage, LocalGroupPage, LocalGroup


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


@hooks.register("before_delete_page")
@hooks.register("before_copy_page")
def protect_base_and_local_group_pages(request, page):
    if request.user.is_superuser:
        return

    if isinstance(page.specific, LocalGroupPage):
        if page.group.is_regional_group:
            return permission_denied(request)


# WagtailMenus: Show menu edit infos in a custom template


class XrMainMenuEditView(MainMenuEditView):
    def get_template_names(self):
        return ["modeladmin/wagtailmenus/mainmenu/edit.html"]


class XrMainMenuAdmin(MainMenuAdmin):
    # edit_template_name = "modeladmin/wagtailmenus/mainmenu/edit.html"
    edit_view_class = XrMainMenuEditView


# Editor interface


@hooks.register("insert_editor_js")
def editor_js():
    return format_html(
        '<script src="{0}"></script>'.format(static("js/wagtail_editor.js"))
    )


@hooks.register("insert_editor_css")
def editor_css():
    return format_html(
        '<link rel="stylesheet" href="{0}">'.format(static("styles/wagtail_editor.css"))
    )
