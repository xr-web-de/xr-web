from django import template
from django.utils.text import normalize_newlines
from wagtailmenus.models import FlatMenu

from xr_pages import services

register = template.Library()


@register.simple_tag(takes_context=True)
def get_site(context):
    request = context.get("request", None)
    return services.get_site(request)


@register.simple_tag(takes_context=True)
def get_home_page(context):
    request = context.get("request", None)
    return services.get_home_page(request)


@register.simple_tag(takes_context=True)
def get_local_group_list_page(context):
    request = context.get("request", None)
    return services.get_local_group_list_page(request)


@register.simple_tag(takes_context=True)
def get_local_groups(context):
    request = context.get("request", None)
    return services.get_local_groups


@register.inclusion_tag("xr_pages/templatetags/inline_svg_text.html")
def inline_svg_text(text, font_size=30):
    text = normalize_newlines(text)

    text_lines = text.split("\n")

    return {"text_lines": text_lines, "font_size": font_size}


@register.simple_tag(takes_context=True)
def get_footer_menus(context):
    try:
        site = context["request"].site
        footer_menus = FlatMenu.objects.filter(handle__startswith="footer_", site=site)
    except (KeyError, AttributeError):
        return None
    return list(footer_menus)
