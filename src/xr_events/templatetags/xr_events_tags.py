from django import template

from xr_events import services


register = template.Library()


@register.simple_tag(takes_context=True)
def get_event_list_page(context):
    request = context.get("request", None)
    return services.get_event_list_page(request)


@register.simple_tag(takes_context=True)
def get_event_group_pages(context):
    request = context.get("request", None)
    return services.get_event_group_pages(request, only_with_active_events=False)


@register.simple_tag(takes_context=True)
def get_active_event_group_pages(context):
    request = context.get("request", None)
    return services.get_event_group_pages(request, only_with_active_events=True)
