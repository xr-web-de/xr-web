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
    list_display = ("title", "dates_display", "location", "organiser_display")
    # list_filter = ("", )
    search_fields = ("title", "dates__start", "location")

    def dates_display(self, obj):
        dates = [
            formats.date_format(date.start, "SHORT_DATE_FORMAT")
            for date in obj.dates.all()
            if date.start
        ]
        return mark_safe("<br>".join(dates))

    dates_display.short_description = _("Dates")

    def organiser_display(self, obj):
        organisers = [obj.organiser.get("name", "")]
        if hasattr(obj, "further_organisers") and obj.further_organisers.count() > 0:
            organisers += [organiser.name for organiser in obj.further_organisers.all()]
        return mark_safe("<br>".join(organisers))

    organiser_display.short_description = _("Organisers")


modeladmin_register(EventAdmin)
