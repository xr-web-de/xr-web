from condensedinlinepanel.edit_handlers import CondensedInlinePanel
from django.core.exceptions import ValidationError
from django.db import models, transaction
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
from wagtail.core.fields import RichTextField, StreamField
from wagtail.core.models import Orderable, Page, Collection
from wagtail.images.edit_handlers import ImageChooserPanel

from xr_events.services import get_or_create_or_update_auth_group_for_event_group_page
from xr_pages.blocks import simple_rich_text_features, ContentBlock
from xr_pages.models import HomePage
from xr_pages.services import (
    add_group_page_permission,
    add_group_collection_permission,
    get_document_permission,
    get_image_permission,
)


class EventPage(Page):
    template = "xr_events/pages/event_detail.html"
    image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    description = RichTextField(
        features=simple_rich_text_features,
        blank=True,
        help_text=_("The description is only visible on the detail page."),
    )
    location = models.CharField(max_length=255, blank=True)

    content_panels = Page.content_panels + [
        ImageChooserPanel("image"),
        FieldPanel("description", classname="full"),
        FieldPanel("location"),
        CondensedInlinePanel("dates", label=_("Dates")),
        CondensedInlinePanel("further_organisers", label=_("Further organisers")),
    ]

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
            .order_by("-dates__start", "title")
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

    content_panels = Page.content_panels + [StreamFieldPanel("content")]
    settings_panels = Page.settings_panels + [
        MultiFieldPanel(
            [PageChooserPanel("local_group", "xr_pages.LocalGroupPage")],
            heading=_("Event Group settings"),
        )
    ]

    parent_page_types = ["EventListPage"]

    def clean(self):
        if self.local_group and self.is_regional_group:
            message = _("This is the regional group. You can't select a local group.")
            raise ValidationError(message)

        elif not self.local_group and not self.is_regional_group:
            message = _('Please choose a "local group" from the settings tab.')
            raise ValidationError(message)

        event_group_page_exists = (
            EventGroupPage.objects.filter(local_group=self.local_group)
            .exclude(pk=self.pk)
            .exists()
        )
        if event_group_page_exists:
            message = _(
                "There exists already an EventGroupPage for the choosen local group. "
                "Please choose another local group."
            )
            raise ValidationError(message)

    @transaction.atomic
    def save(self, *args, **kwargs):
        is_new = self.id is None

        super().save(*args, **kwargs)

        moderators_group = get_or_create_or_update_auth_group_for_event_group_page(
            self, "Event Moderators"
        )
        editors_group = get_or_create_or_update_auth_group_for_event_group_page(
            self, "Event Editors"
        )

        # we only need to add permissions on page creation
        if is_new:
            collection = Collection.objects.get(name="Common")

            # Moderators
            for permission_type in ["add", "edit", "publish"]:
                add_group_page_permission(moderators_group, self, permission_type)

            for codename in ["add_document", "change_document", "delete_document"]:
                add_group_collection_permission(
                    moderators_group, collection, get_document_permission(codename)
                )
            for codename in ["add_image", "change_image", "delete_image"]:
                add_group_collection_permission(
                    moderators_group, collection, get_image_permission(codename)
                )

            # Editors
            for permission_type in ["add", "edit"]:
                add_group_page_permission(editors_group, self, permission_type)

            add_group_collection_permission(
                editors_group, collection, get_document_permission("add_document")
            )
            add_group_collection_permission(
                editors_group, collection, get_image_permission("add_image")
            )

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        context["events"] = (
            EventPage.objects.child_of(self).live().order_by("-dates__start", "title")
        )
        return context

    @property
    def organiser(self):
        if self.is_regional_group:
            home_page = HomePage.objects.ancestor_of(self).live().first()
            return {
                "name": home_page.xr_group_name,
                "email": home_page.group_email,
                "url": home_page.get_url(),
                "events_url": self.get_url(),
            }
        elif self.local_group:
            local_group = self.local_group.specific
            return {
                "name": local_group.xr_name,
                "email": local_group.email,
                "url": local_group.get_url(),
                "events_url": self.get_url(),
            }
        return None
