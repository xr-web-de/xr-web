from django import template

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
        local_group_page = context.get("page", None).group.local_group_page
    except (KeyError, AttributeError):
        return None
    return local_group_page
