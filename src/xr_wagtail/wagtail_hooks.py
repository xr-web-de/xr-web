from django.templatetags.static import static
from django.urls import reverse
from django.utils.html import format_html
from wagtail.admin.menu import MenuItem
from wagtail.core import hooks


# Wagtail editor interface
from wagtailmenus.modeladmin import MainMenuAdmin
from wagtailmenus.views import MainMenuEditView


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


# Wagtail global admin
@hooks.register("insert_global_admin_css")
def global_admin_css():
    return format_html(
        '<link rel="stylesheet" href="{0}">'.format(
            static("styles/wagtail_global_admin.css")
        )
    )


class SuperuserMenuItem(MenuItem):
    def is_shown(self, request):
        return request.user.is_superuser


@hooks.register("register_settings_menu_item")
def register_remove_revisions_for_all_pages_menu_item():
    return SuperuserMenuItem(
        "Remove old revisions",
        reverse("remove_old_revisions_for_all_pages"),
        classnames="icon icon-bin",
        order=10000,
    )


# WagtailMenus: Add help/info text
class XrMainMenuEditView(MainMenuEditView):
    def get_template_names(self):
        return ["modeladmin/wagtailmenus/mainmenu/edit.html"]


class XrMainMenuAdmin(MainMenuAdmin):
    edit_view_class = XrMainMenuEditView
