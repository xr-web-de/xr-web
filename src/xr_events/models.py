from django.db import models
from django.db.models import Q, QuerySet
from django.utils import formats
from django.utils.timezone import localdate
from django.utils.translation import ugettext as _
from modelcluster.fields import ParentalKey
from wagtail.admin.edit_handlers import (
    FieldPanel,
    FieldRowPanel,
    HelpPanel,
    StreamFieldPanel,
    PageChooserPanel,
)
from wagtail.core.fields import StreamField
from wagtail.core.models import Orderable, PageManager, Page
from wagtail.core.query import PageQuerySet
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.snippets.edit_handlers import SnippetChooserPanel
from condensedinlinepanel.edit_handlers import CondensedInlinePanel

from xr_pages.blocks import ContentBlock
from xr_pages.models import LocalGroup, XrPage
from django.template.response import TemplateResponse


"""
A little helper class for common things
on EventListing pages (shared by EventListPage
and EventGroupPage).
"""


class EventPageListFilter:

    """
    Creates a queryset with objects of the page given through xrEventPage
    and parses the given request for a valid range to filter the list.
    Adds the filtered_events, the timefilter-definition and the selected
    value to the context for easy access within the template.
    """

    @staticmethod
    def get_timefilter_and_selected_days(data):
        # parse GET request
        get_d = data.get("d", 30)

        if get_d == "365":
            days = 365
        elif get_d == "182":
            days = 182
        elif get_d == "-30":
            days = -30
        elif get_d == "0":
            days = 0
        else:
            days = 30

        # used to built the list of selectable time filters in the template
        timefilter = {
            "30": _("Next month"),
            "182": _("Next six months"),
            "365": _("Next Year"),
            "0": _("All upcoming"),
            "-30": _("Last month"),
        }

        return timefilter, days


class EventPageQuerySet(PageQuerySet):
    def upcoming(self):
        return self.filter(end_date__isnull=False, end_date__gte=localdate())

    def previous(self):
        return self.filter(start_date__isnull=False, start_date__lte=localdate())

    def date_range(self, date_range):
        from_date, to_date = date_range

        return self.filter(
            start_date__isnull=False,
            end_date__isnull=False,
            end_date__gte=from_date,
            start_date__lte=to_date,
        )


EventPageManager = PageManager.from_queryset(EventPageQuerySet)


class EventPage(XrPage):
    template = "xr_events/pages/event_detail.html"
    content = StreamField(
        ContentBlock,
        blank=True,
        help_text=_("The content is only visible on the detail page."),
    )
    location = models.CharField(
        max_length=255,
        blank=True,
        help_text=_(
            "Some city or address, like you would enter in GMaps or OpenStreetMap, "
            'e.g. "Berlin", "Somestreet 84, 12345 Samplecity".'
        ),
    )
    group = models.ForeignKey(
        LocalGroup, on_delete=models.PROTECT, editable=False, related_name="events"
    )
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)

    content_panels = XrPage.content_panels + [
        CondensedInlinePanel("dates", label=_("Dates")),
        FieldPanel("location"),
        CondensedInlinePanel("further_organisers", label=_("Further organisers")),
        StreamFieldPanel("content"),
    ]

    parent_page_types = ["EventGroupPage"]

    objects = EventPageManager()

    is_event_page = True

    class Meta:
        verbose_name = _("Event")
        verbose_name_plural = _("Events")

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        context["event"] = self
        return context

    def get_image(self):
        if self.image:
            return self.image
        event_group_page = EventGroupPage.objects.ancestor_of(self).last()
        if event_group_page.default_event_image:
            return event_group_page.default_event_image
        event_list_page = EventListPage.objects.ancestor_of(self).last()
        if event_list_page.default_event_image:
            return event_list_page.default_event_image
        return None

    @property
    def organiser(self):
        return self.group

    def get_all_organisers(self):
        all_organisers = [self.group]
        shadow_qs = self.shadow_events.live().filter(original_event=self)
        if shadow_qs.exists():
            all_organisers += [shadow.specific.group for shadow in shadow_qs]
        if hasattr(self, "further_organisers") and self.further_organisers.exists():
            all_organisers += list(self.further_organisers.all())
        return all_organisers

    @property
    def all_organiser_names(self):
        return ", ".join([organiser.name for organiser in self.get_all_organisers()])

    def save(self, *args, **kwargs):
        if not hasattr(self, "group"):
            self.group = self.get_parent().specific.group

        if self.dates.exists():
            all_dates = []
            for date in self.dates.all():
                all_dates.append(date.start)
                if date.end:
                    all_dates.append(date.end)
            all_dates = sorted(all_dates)
            self.start_date = all_dates[0]
            self.end_date = all_dates[-1]

        super().save(*args, **kwargs)


class ShadowEventPageQuerySet(PageQuerySet):
    def upcoming(self):
        return self.filter(
            original_event__isnull=False,
            original_event__end_date__isnull=False,
            original_event__end_date__gte=localdate(),
        )

    def previous(self):
        return self.filter(
            original_event__isnull=False,
            original_event__start_date__isnull=False,
            original_event__start_date__lte=localdate(),
        )

    def date_range(self, date_range):
        from_date, to_date = date_range
        return self.filter(
            original_event__isnull=False,
            original_event__start_date__isnull=False,
            original_event__end_date__isnull=False,
            original_event__end_date__gte=from_date,
            original_event__start_date__lte=to_date,
        )


ShadowEventPageManager = PageManager.from_queryset(ShadowEventPageQuerySet)


class ShadowEventPage(Page):
    template = "xr_events/pages/event_detail.html"
    group = models.ForeignKey(
        LocalGroup,
        on_delete=models.PROTECT,
        editable=False,
        related_name="shadow_events",
    )
    original_event = models.ForeignKey(
        EventPage,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="shadow_events",
    )

    content_panels = Page.content_panels + [
        PageChooserPanel("original_event", EventPage)
    ]

    is_event_page = True

    parent_page_types = ["EventGroupPage"]

    objects = ShadowEventPageManager()

    class Meta:
        verbose_name = _("Shadow Event")
        verbose_name_plural = _("Shadow Events")

    def get_shadowed_event(self):
        event = self.original_event.specific

        all_organisers = [self.group, event.group]

        shadow_qs = (
            self.original_event.shadow_events.live()
            .filter(original_event=self.original_event)
            .exclude(pk=self.pk)
        )

        if shadow_qs.exists():
            all_organisers += [shadow.specific.group for shadow in shadow_qs]

        if (
            hasattr(self.original_event, "further_organisers")
            and self.original_event.further_organisers.exists()
        ):
            all_organisers += list(self.original_event.further_organisers.all())

        event.get_all_organisers = lambda: all_organisers
        event.group = self.group
        event.get_url = self.get_url

        return event

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        context["event"] = self.get_shadowed_event()
        return context

    def save(self, *args, **kwargs):
        if not hasattr(self, "group"):
            self.group = self.get_parent().specific.group

        super().save(*args, **kwargs)


class EventDateQuerySet(QuerySet):
    def live(self):
        return self.filter(event_page__live=True)

    def start_before(self, date):
        return self.filter(start__date__lte=date)

    def end_after(self, date):
        return self.filter(
            Q(end__isnull=False) & Q(end__date__gte=date) | Q(start__date__gte=date)
        )

    def upcoming(self):
        return self.end_after(localdate())

    def previous(self):
        return self.start_before(localdate())

    def date_range(self, date_range):
        from_date, to_date = date_range
        return self.end_after(from_date).start_before(to_date)

    def for_group(self, group):
        return self.filter(
            Q(event_page__group=group) | Q(event_page__shadow_events__group=group)
        )


EventDateManager = PageManager.from_queryset(EventDateQuerySet)


class EventDate(Orderable):
    event_page = ParentalKey(EventPage, on_delete=models.CASCADE, related_name="dates")
    start = models.DateTimeField()
    end = models.DateTimeField(null=True, blank=True)
    label = models.CharField(
        blank=True,
        max_length=255,
        help_text=_('Optional label like "Part I" or "Meeting point"'),
    )
    location = models.CharField(
        max_length=255,
        blank=True,
        help_text=_(
            "A more specific location, overwrites the events default location."
        ),
    )
    description = models.CharField(
        max_length=1000,
        blank=True,
        help_text=_("Optional date description. Visible on event detail page only."),
    )

    panels = [
        FieldRowPanel([FieldPanel("start"), FieldPanel("end")]),
        FieldRowPanel([FieldPanel("label"), FieldPanel("location")]),
        FieldPanel("description"),
    ]

    objects = EventDateQuerySet.as_manager()

    class Meta:
        verbose_name = _("Date")
        verbose_name_plural = _("Dates")
        ordering = ["start", "sort_order"]

    def __str__(self):
        start = formats.date_format(self.start, "SHORT_DATETIME_FORMAT")
        if not self.label:
            return "{}".format(start)
        return "{} | {}".format(start, self.label)


class EventOrganiser(Orderable):
    event_page = ParentalKey(
        EventPage, on_delete=models.CASCADE, related_name="further_organisers"
    )
    name = models.CharField(max_length=255, blank=True)
    email = models.EmailField(blank=True)
    url = models.URLField(blank=True)

    panels = [
        HelpPanel(
            "<p>%s</p>"
            % _(
                "If the event is organised in cooperation with other groups, name them here."
            )
        ),
        FieldRowPanel([FieldPanel("name"), FieldPanel("email")]),
        FieldRowPanel([FieldPanel("url")]),
    ]

    class Meta:
        verbose_name = _("Organiser")
        verbose_name_plural = _("Organisers")
        ordering = ["sort_order"]

    def __str__(self):
        return self.name


class EventListPage(XrPage):
    template = "xr_events/pages/event_list.html"
    content = StreamField(ContentBlock, blank=True)
    group = models.OneToOneField(LocalGroup, editable=False, on_delete=models.PROTECT)
    default_event_image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text=_("A default image as Fallback for events, that have no image."),
    )

    content_panels = XrPage.content_panels + [StreamFieldPanel("content")]

    settings_panels = XrPage.settings_panels + [
        ImageChooserPanel("default_event_image")
    ]

    parent_page_types = []
    is_creatable = False

    """
    Override serve method to filter based on request params
    """

    def serve(self, request, *args, **kwargs):
        from xr_events.services import date_range_from_days

        timefilter, selected = EventPageListFilter.get_timefilter_and_selected_days(
            request.GET
        )

        date_range = date_range_from_days(selected)

        event_dates = EventDate.objects.live().date_range(date_range)

        context = self.get_context(request, *args, **kwargs)
        context.update(
            {
                "event_dates": event_dates,
                # "events_by_date": events_by_date,
                "timefilter": timefilter,
                "selected": str(selected),
            }
        )
        return TemplateResponse(request, self.template, context)

    class Meta:
        verbose_name = _("Event List Page")
        verbose_name_plural = _("Event List Pages")


class EventGroupPage(XrPage):
    template = "xr_events/pages/event_group.html"
    content = StreamField(ContentBlock, blank=True)
    group = models.OneToOneField(LocalGroup, on_delete=models.PROTECT)
    default_event_image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text=_("A default image as Fallback for events, that have no image."),
    )

    content_panels = XrPage.content_panels + [
        SnippetChooserPanel("group"),
        StreamFieldPanel("content"),
    ]

    settings_panels = XrPage.settings_panels + [
        ImageChooserPanel("default_event_image")
    ]

    parent_page_types = ["EventListPage"]

    """
    Override serve method to filter based on request params
    """

    def serve(self, request, *args, **kwargs):
        from xr_events.services import date_range_from_days

        timefilter, selected = EventPageListFilter.get_timefilter_and_selected_days(
            request.GET
        )

        date_range = date_range_from_days(selected)

        event_dates = EventDate.objects.live().date_range(date_range)

        context = self.get_context(request, *args, **kwargs)
        context.update(
            {
                "event_dates": event_dates,
                # "events_by_date": events_by_date,
                "timefilter": timefilter,
                "selected": str(selected),
            }
        )
        return TemplateResponse(request, self.template, context)

    class Meta:
        verbose_name = _("Event Group Page")
        verbose_name_plural = _("Event Group Pages")
