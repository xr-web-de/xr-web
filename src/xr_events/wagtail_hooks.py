from django.db.models import Min, F
from django.utils import formats
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _
from wagtail.admin.utils import permission_denied
from wagtail.contrib.modeladmin.options import ModelAdmin, modeladmin_register
from wagtail.core import hooks

from .models import EventPage, EventGroupPage, EventListPage


class EventAdmin(ModelAdmin):
    model = EventPage
    menu_label = "Events"
    menu_icon = "date"
    menu_order = 100  # 000 being 1st, 100 2nd, 200 3rd
    add_to_settings_menu = False
    exclude_from_explorer = False
    list_display = (
        "title",
        "get_dates_display",
        "location",
        "get_organiser_display",
        "get_further_organisers_display",
    )
    list_filter = ("group",)
    search_fields = ("title", "dates__start", "location", "further_organisers__name")

    def get_queryset(self, request):
        # we overwrite this method to annotate fields before ordering is applied
        # note that self.ordering or self.get_ordering() will have no effect
        qs = self.model._default_manager.get_queryset()
        qs = qs.annotate(start_date=Min("dates__start"))
        return qs.order_by(F("start_date").desc(nulls_last=True), "title")

    def get_dates_display(self, obj):
        dates = [
            formats.date_format(date.start, "SHORT_DATE_FORMAT")
            for date in obj.dates.all()
            if date.start
        ]
        return mark_safe("<br>".join(dates))

    get_dates_display.short_description = _("Dates")

    def get_organiser_display(self, obj):
        if obj.group.is_regional_group:
            return "%s<br>(%s)" % (obj.group.name, _("transregional"))
        return obj.group.name

    get_organiser_display.short_description = _("Organiser")

    def get_further_organisers_display(self, obj):
        organisers = []
        if hasattr(obj, "further_organisers") and obj.further_organisers.count() > 0:
            organisers = [
                str(organiser)
                for organiser in obj.further_organisers.all().order_by("sort_order")
            ]
        return mark_safe("<br>".join(organisers))

    get_further_organisers_display.short_description = _("Further Organisers")


modeladmin_register(EventAdmin)


@hooks.register("before_create_page")
@hooks.register("before_delete_page")
@hooks.register("before_copy_page")
def protect_event_group_pages(request, page):
    if request.user.is_superuser:
        return

    if isinstance(page.specific, EventListPage):
        return permission_denied(request)

    if isinstance(page.specific, EventGroupPage):
        if page.is_regional_group:
            return permission_denied(request)
