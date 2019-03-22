from django import template
from wagtail.core.models import Page

from ..models import LocalGroupListPage, LocalGroupPage

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
    except LocalGroupListPage.DoesNotExist:
        return None
    return local_group_list_page


@register.simple_tag()
def get_local_group_page_for(page):
    if not issubclass(type(page), Page):
        raise ValueError(
            "get_local_group_page_for tag expected a subclass of Page, got %r"
            % type(page).__name__
        )
    try:
        local_group_page = (
            LocalGroupPage.objects.ancestor_of(page, inclusive=True).live().get()
        )
    except LocalGroupPage.DoesNotExist:
        raise ValueError(
            "There is no LocalGroupPage ancestor of the given Page object %r" % page
        )
    return local_group_page
