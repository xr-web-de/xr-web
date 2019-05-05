import os

from django import template
from django.conf import settings
from django.template import Template, Context
from django.utils.safestring import mark_safe
from django.utils.text import normalize_newlines
from wagtailmenus.models import FlatMenu

from xr_pages import services
from xr_pages.svg_icons import svg_icon_map

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


@register.simple_tag()
def svg_icon(icon_name, size=32, css_classes="", aria_label=""):
    if icon_name not in svg_icon_map:
        return ""
    icon_filename = svg_icon_map[icon_name]
    icon_directory = "xr_pages/svg_icons/icons/"

    icon_path = os.path.join(settings.BASE_DIR, icon_directory, icon_filename)

    if not os.path.isfile(icon_path):
        return ""

    template = Template(
        """
        <i class="svg-container {{ css_classes }}"
            style="width:{{ size }}px; height:{{ size }}px"
            {% if aria_label %}
                aria-label="{{ aria_label }}"
                aria-hidden="true"
            {% endif %}
        >{{ svg }}</i>
    """
    )

    with open(icon_path) as svg_file:
        context = Context(
            {
                "svg": mark_safe(svg_file.read()),
                "size": size,
                "css_classes": css_classes,
                "aria_label": aria_label,
            }
        )

    html = template.render(context)

    return html
