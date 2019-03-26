from django.db.models import Min, F
from django.utils import formats
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _
from wagtail.admin.utils import permission_denied
from wagtail.contrib.modeladmin.options import ModelAdmin, modeladmin_register
from wagtail.core import hooks

from .models import EventPage, EventGroupPage


class EventAdmin(ModelAdmin):
    model = EventPage
    menu_label = "Events"
    menu_icon = "date"
    menu_order = 100  # 000 being 1st, 100 2nd, 200 3rd
    add_to_settings_menu = False
    exclude_from_explorer = False
    list_display = ("title", "get_dates_display", "location", "get_organisers_display")
    list_filter = ("group", "start_date")
    search_fields = (
        "title",
        "start_date",
        "end_date",
        "location",
        "group__name",
        "further_organisers__name",
    )

    def get_queryset(self, request):
        # we overwrite this method to annotate fields before ordering is applied
        # note that self.ordering or self.get_ordering() will have no effect
        qs = self.model._default_manager.get_queryset()
        return qs.order_by(F("start_date").desc(nulls_last=True), "title")

    def get_dates_display(self, obj):
        dates = []
        if obj.start_date:
            start = formats.date_format(obj.start_date, "SHORT_DATE_FORMAT")
            dates.append(start)
        if obj.end_date:
            end = formats.date_format(obj.end_date, "SHORT_DATE_FORMAT")
            dates.append(end)
        return mark_safe("<br>".join(dates))

    get_dates_display.short_description = _("Dates")

    def get_organisers_display(self, obj):
        organisers = [obj.group.name]
        if obj.further_organisers.exists():
            for organiser in obj.further_organisers.all().order_by("sort_order"):
                organisers.append(str(organiser))
        return mark_safe("<br>".join(organisers))

    get_organisers_display.short_description = _("Organisers")


modeladmin_register(EventAdmin)


@hooks.register("before_delete_page")
@hooks.register("before_copy_page")
def protect_event_group_pages(request, page):
    if request.user.is_superuser:
        return

    if isinstance(page.specific, EventGroupPage):
        if page.is_regional_group:
            return permission_denied(request)
