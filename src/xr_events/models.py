from condensedinlinepanel.edit_handlers import CondensedInlinePanel
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import F, Min
from django.utils import formats
from django.utils.translation import ugettext as _
from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel
from wagtail.admin.edit_handlers import (
    FieldPanel,
    PageChooserPanel,
    MultiFieldPanel,
    FieldRowPanel,
    HelpPanel,
    StreamFieldPanel,
)
from wagtail.core.fields import StreamField
from wagtail.core.models import Orderable, Page, Collection
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.snippets.edit_handlers import SnippetChooserPanel

from xr_pages.blocks import ContentBlock
from xr_pages.models import HomePage, LocalGroup


class EventPage(Page):
    template = "xr_events/pages/event_detail.html"
    image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text=_(
            "An image that can be used not only for the detail view, but also for "
            "lists, teasers or social media."
        ),
    )
    description = models.CharField(
        max_length=254,
        default="",
        blank=True,
        help_text=_(
            "A description not only for the detail view, but also for lists, "
            "teasers or social media."
        ),
    )
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
        LocalGroup,
        null=True,
        on_delete=models.PROTECT,
        editable=False,
        related_name="events",
    )

    content_panels = Page.content_panels + [
        ImageChooserPanel("image"),
        FieldPanel("description", classname="full"),
        FieldPanel("location"),
        CondensedInlinePanel("dates", label=_("Dates")),
        CondensedInlinePanel("further_organisers", label=_("Further organisers")),
        StreamFieldPanel("content"),
    ]
    promote_panels = Page.promote_panels + []

    parent_page_types = ["EventGroupPage"]

    class Meta:
        verbose_name = _("Event")
        verbose_name_plural = _("Events")

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        context["event"] = self
        return context

    @property
    def event_group(self):
        return EventGroupPage.objects.parent_of(self).live().first()

    @property
    def local_group(self):
        return self.event_group.local_group

    @property
    def organiser(self):
        return self.event_group.organiser

    def save(self, *args, **kwargs):
        is_new = self.id is None

        if is_new:
            self.group = self.get_parent().specific.group

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

    def __str__(self):
        return self.name


class EventListPage(Page):
    template = "xr_events/pages/event_list.html"
    content = StreamField(ContentBlock, blank=True)

    content_panels = Page.content_panels + [StreamFieldPanel("content")]

    parent_page_types = []
    is_creatable = False

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        context["events"] = (
            EventPage.objects.descendant_of(self)
            .live()
            .annotate(start_date=Min("dates__start"))
            .order_by(F("start_date").desc(nulls_last=True), "title")
        )
        context["event_groups"] = (
            EventGroupPage.objects.child_of(self).live().order_by("title")
        )
        return context


class EventGroupPage(Page):
    template = "xr_events/pages/event_group.html"
    content = StreamField(ContentBlock, blank=True)
    local_group = models.ForeignKey(
        "wagtailcore.Page",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="event_group_set",
    )
    is_regional_group = models.BooleanField(editable=False, default=False)
    group = models.OneToOneField(LocalGroup, null=True, on_delete=models.PROTECT)

    content_panels = Page.content_panels + [
        SnippetChooserPanel("group"),
        StreamFieldPanel("content"),
    ]
    settings_panels = Page.settings_panels + [
        MultiFieldPanel(
            [PageChooserPanel("local_group", "xr_pages.LocalGroupPage")],
            heading=_("Event Group settings"),
        )
    ]

    parent_page_types = ["EventListPage"]

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        context["events"] = (
            EventPage.objects.child_of(self).live().order_by("-dates__start", "title")
        )
        return context

    @property
    def organiser(self):
        return self.group

    def clean(self):
        if not self.group:
            message = _('Please select a "group".')
            raise ValidationError(message)
