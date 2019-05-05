from condensedinlinepanel.edit_handlers import CondensedInlinePanel
from django.db import models
from django.utils import formats
from django.utils.timezone import localdate
from django.utils.translation import ugettext as _
from modelcluster.fields import ParentalKey
from wagtail.admin.edit_handlers import (
    FieldPanel,
    FieldRowPanel,
    HelpPanel,
    StreamFieldPanel,
)
from wagtail.core.fields import StreamField
from wagtail.core.models import Orderable, Page, PageManager
from wagtail.core.query import PageQuerySet
from wagtail.snippets.edit_handlers import SnippetChooserPanel

from xr_pages.blocks import ContentBlock
from xr_pages.models import LocalGroup, XrPage


class EventPageQuerySet(PageQuerySet):
    def upcoming(self):
        return self.filter(end_date__isnull=False).filter(end_date__gte=localdate())

    def previous(self):
        return self.filter(start_date__isnull=False).filter(start_date__lte=localdate())


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

    content_panels = Page.content_panels + [
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

    @property
    def organiser(self):
        return self.group

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


class EventDate(Orderable):
    event_page = ParentalKey(EventPage, on_delete=models.CASCADE, related_name="dates")
    start = models.DateTimeField()
    end = models.DateTimeField(null=True, blank=True)
    label = models.CharField(
        blank=True,
        max_length=255,
        help_text=_('Optional label like "Part I" or "Meeting point"'),
    )

    panels = [
        FieldRowPanel([FieldPanel("start"), FieldPanel("end")]),
        FieldPanel("label"),
    ]

    class Meta:
        verbose_name = _("Date")
        verbose_name_plural = _("Dates")

    def __str__(self):
        start = formats.date_format(self.start, "SHORT_DATETIME_FORMAT")
        if not self.label:
            return start
        return "%s | %s" % (start, self.label)


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

    def __str__(self):
        return self.name


class EventListPage(XrPage):
    template = "xr_events/pages/event_list.html"
    content = StreamField(ContentBlock, blank=True)

    content_panels = Page.content_panels + [StreamFieldPanel("content")]

    parent_page_types = []
    is_creatable = False

    class Meta:
        verbose_name = _("Event List Page")
        verbose_name_plural = _("Event List Pages")

    @property
    def upcoming_events(self):
        return (
            EventPage.objects.live()
            .descendant_of(self)
            .upcoming()
            .order_by("start_date", "title")
        )

    @property
    def previous_events(self):
        return (
            EventPage.objects.live()
            .descendant_of(self)
            .previous()
            .order_by("-start_date", "title")
        )


class EventGroupPage(XrPage):
    template = "xr_events/pages/event_group.html"
    content = StreamField(ContentBlock, blank=True)
    group = models.OneToOneField(LocalGroup, on_delete=models.PROTECT)

    content_panels = Page.content_panels + [
        SnippetChooserPanel("group"),
        StreamFieldPanel("content"),
    ]

    parent_page_types = ["EventListPage"]

    class Meta:
        verbose_name = _("Event Group Page")
        verbose_name_plural = _("Event Group Pages")

    @property
    def organiser(self):
        return self.group

    @property
    def is_regional_group(self):
        return self.group.is_regional_group

    @property
    def upcoming_events(self):
        return (
            EventPage.objects.live()
            .child_of(self)
            .upcoming()
            .order_by("start_date", "title")
        )

    @property
    def previous_events(self):
        return (
            EventPage.objects.live()
            .child_of(self)
            .previous()
            .order_by("-start_date", "title")
        )
