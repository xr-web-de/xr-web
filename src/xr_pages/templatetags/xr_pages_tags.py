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
def inline_svg_text(text, font_size=None):
    text = normalize_newlines(text)

    text_lines = text.split("\n")

    return {
        "text_lines": text_lines,
        "font_size": font_size,
        "text_y": "{}".format(len(text_lines) / 2),
    }


@register.simple_tag(takes_context=True)
def get_footer_menus(context):
    try:
        site = context["request"].site
        footer_menus = FlatMenu.objects.filter(handle__startswith="footer_", site=site)
    except (KeyError, AttributeError):
        return None
    return list(footer_menus)


@register.simple_tag(takes_context=True)
def svg_icon(context, icon_name, size=32, css_classes="", aria_label=""):
    if icon_name not in svg_icon_map:
        return ""

    embedded_svg_icons = context.get("_embedded_svg_icons", set())
    svg_context = Context(
        {
            "name": icon_name,
            "size": size,
            "css_classes": css_classes,
            "aria_label": aria_label,
        }
    )

    if icon_name in embedded_svg_icons:
        # The icon was already embedded. Render a <use> tag instead.
        svg_context["svg"] = mark_safe(
            '<svg viewbox="0 0 100 100"><use href="#svg-icon-{name}"/></svg>'.format(
                name=icon_name
            )
        )

    else:
        # The icon is not yet embedded. Render the svg.
        icon_filename = svg_icon_map[icon_name]
        icon_directory = "xr_pages/svg_icons/icons/"

        icon_path = os.path.join(settings.BASE_DIR, icon_directory, icon_filename)

        if not os.path.isfile(icon_path):
            return ""

        with open(icon_path) as svg_file:
            svg_context["svg"] = mark_safe(svg_file.read())

        # Remember, that we already embedded this svg icon.
        # Every time we render with the same context, the icon won't be embedded again but a <use> tag will be rendered instead.
        embedded_svg_icons.add(icon_name)
        context["_embedded_svg_icons"] = embedded_svg_icons

    svg_template = Template(
        """
        <i class="svg-container svg-container__{{ name }} {{ css_classes }}"
            style="width:{{ size }}px; height:{{ size }}px"
            {% if aria_label %}
                aria-label="{{ aria_label }}"
                aria-hidden="true"
            {% endif %}
        >{{ svg }}</i>
    """
    )
    html = svg_template.render(svg_context)

    return html


@register.inclusion_tag("xr_pages/templatetags/social_media_page_links.html")
def render_social_media_links_for_group(
    group, size=32, css_classes="", show_label=False
):

    social_media_links = []

    for attr_name in ["facebook", "twitter", "youtube", "instagram", "mastodon"]:
        url = None
        if hasattr(group, attr_name):
            url = getattr(group, attr_name)

        if url:
            social_media_links.append(
                {
                    "url": url,
                    "icon_name": attr_name,
                    "verbose_name": attr_name.capitalize(),
                }
            )

    return {
        "social_media_links": social_media_links,
        "size": size,
        "css_classes": css_classes,
        "show_label": show_label,
    }
