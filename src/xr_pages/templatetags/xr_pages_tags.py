from django import template
from django.utils.text import normalize_newlines
from wagtailmenus.models import FlatMenu

from ..models import LocalGroupListPage

register = template.Library()


@register.simple_tag(takes_context=True)
def get_site(context):
    try:
        site = context["request"].site
    except (KeyError, AttributeError):
        return None
    return site


@register.simple_tag(takes_context=True)
def get_home_page(context):
    try:
        home_page = context["request"].site.root_page.specific
    except (KeyError, AttributeError):
        return None
    return home_page


@register.simple_tag(takes_context=True)
def get_local_group_list_page(context):
    try:
        home_page = context["request"].site.root_page
        local_group_list_page = (
            LocalGroupListPage.objects.child_of(home_page).live().get()
        )
    except (KeyError, AttributeError, LocalGroupListPage.DoesNotExist):
        return None
    return local_group_list_page


@register.simple_tag(takes_context=True)
def get_local_group_page_for(context, page=None):
    try:
        local_group_page = context.get("page", None).group.localgrouppage.specific
    except (KeyError, AttributeError):
        return None
    return local_group_page


@register.inclusion_tag("xr_pages/templatetags/inline_svg_text.html")
def inline_svg_text(message, font_size=30):
    message = normalize_newlines(message)

    message_lines = message.split("\n")

    return {"message_lines": message_lines, "font_size": font_size}


@register.simple_tag(takes_context=True)
def get_footer_menus(context):
    try:
        site = context["request"].site
        footer_menus = FlatMenu.objects.filter(handle__startswith="footer_", site=site)
    except (KeyError, AttributeError):
        return None
    return list(footer_menus)
