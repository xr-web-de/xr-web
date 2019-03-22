import json

from django.db.models import Min, F
from django.utils import formats
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _
from wagtail.contrib.modeladmin.options import ModelAdmin, modeladmin_register
from .models import EventPage


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
    list_filter = ("dates__start",)
    search_fields = ("title", "dates__start", "location", "further_organisers__name")

    def get_queryset(self, request):
        # we overwrite this method to annotate fields before ordering is applied
        qs = self.model._default_manager.get_queryset()
        qs = qs.annotate(start_date=Min("dates__start"))

        # ordering = self.get_ordering(request)
        # if ordering:
        #     qs = qs.order_by(*ordering)
        # return qs

        return qs.order_by(F("start_date").desc(nulls_last=True))

    def get_dates_display(self, obj):
        dates = [
            formats.date_format(date.start, "SHORT_DATE_FORMAT")
            for date in obj.dates.all()
            if date.start
        ]
        return mark_safe("<br>".join(dates))

    get_dates_display.short_description = _("Dates")

    def get_organiser_display(self, obj):
        return obj.organiser["name"]

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
