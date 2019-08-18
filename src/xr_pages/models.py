import datetime
from urllib.parse import unquote

from django.db import models, transaction
from django.utils.translation import ugettext as _
from wagtail.admin.edit_handlers import StreamFieldPanel, FieldPanel, MultiFieldPanel
from wagtail.core.fields import StreamField
from wagtail.core.models import Page
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.snippets.edit_handlers import SnippetChooserPanel
from wagtail.snippets.models import register_snippet

from xr_pages.services import get_site
from xr_web.settings import LOCAL_GROUP_STATE_CHOICES
from .blocks import ContentBlock


class XrPage(Page):
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

    # We use this method to allow the opengraph template to get the url 
    # of the image associated with that page.
    # The image is not rendered at another resolution that the original
    # Maybe we want to change that one time...
    def get_image_url(self):
        return self.image.get_rendition('original').url
    
    def get_image_width(self):
        return self.image.get_rendition('original').width
    
    def get_image_height(self):
        return self.image.get_rendition('original').height
    
    description = models.CharField(
        max_length=254,
        default="",
        blank=True,
        help_text=_(
            "A description not only for the detail view, but also for lists, "
            "teasers or social media."
        ),
    )
    show_page_title = models.BooleanField(default=True)

    content_panels = [
        MultiFieldPanel(
            [
                FieldPanel("title", classname="title"),
                FieldPanel("show_page_title", classname=""),
            ],
            heading=_("Title"),
        )
    ]

    promote_panels = Page.promote_panels + [
        ImageChooserPanel("image"),
        FieldPanel("description", classname="full"),
    ]

    class Meta:
        abstract = True


class HomePage(XrPage):
    template = "xr_pages/pages/home.html"
    content = StreamField(ContentBlock, blank=True)
    group = models.OneToOneField("LocalGroup", editable=False, on_delete=models.PROTECT)

    content_panels = XrPage.content_panels + [StreamFieldPanel("content")]

    parent_page_types = []
    is_creatable = False

    class Meta:
        verbose_name = _("Home Page")
        verbose_name_plural = _("Home Pages")


class HomeSubPage(XrPage):
    template = "xr_pages/pages/home_sub.html"
    content = StreamField(ContentBlock, blank=True)
    group = models.ForeignKey("LocalGroup", editable=False, on_delete=models.PROTECT)

    content_panels = XrPage.content_panels + [StreamFieldPanel("content")]

    parent_page_types = ["HomePage", "HomeSubPage"]

    def save(self, *args, **kwargs):
        if not hasattr(self, "group") or self.group is None:
            self.group = self.get_parent().specific.group

        super().save(*args, **kwargs)

    class Meta:
        verbose_name = _("Content Page")
        verbose_name_plural = _("Content Pages")


class LocalGroupQuerySet(models.QuerySet):
    def active(self):
        return self.filter(status=LocalGroup.STATUS_ACTIVE)

    def has_active_localgrouppage(self):
        return self.filter(localgrouppage__isnull=False).filter(
            localgrouppage__live=True
        )

    def has_active_eventgrouppage(self):
        return self.filter(eventgrouppage__isnull=False).filter(
            eventgrouppage__live=True
        )

    def has_active_newsletterformpage(self):
        return self.filter(newsletterformpage__isnull=False).filter(
            newsletterformpage__live=True
        )

    def has_upcoming_events(self):
        return (
            self.filter(events__isnull=False)
            .filter(events__live=True)
            .filter(events__end_date__gte=datetime.date.today)
        )

    def has_previous_events(self):
        return (
            self.filter(events__isnull=False)
            .filter(events__live=True)
            .filter(events__start_date__lte=datetime.date.today)
        )


LocalGroupManager = models.Manager.from_queryset(LocalGroupQuerySet)


class LocalGroup(models.Model):
    site = models.ForeignKey(
        "wagtailcore.Site",
        verbose_name=_("site"),
        db_index=True,
        editable=False,
        on_delete=models.PROTECT,
        related_name="+",
    )
    is_regional_group = models.BooleanField(editable=False, default=False)
    name = models.CharField(
        max_length=50,
        default="",
        unique=True,
        help_text=_(
            "The unique name for the local group. "
            "Used as label for links referring to this page. "
            'Enter a name without leading "XR ".'
        ),
    )
    # old_name field helps with identifying name changes
    old_name = models.CharField(max_length=50, default="", editable=False)
    area_description = models.TextField(
        null=True,
        blank=True,
        help_text=_("More information about the area the group is active in."),
    )
    STATUS_ACTIVE = "active"
    STATUS_IN_FOUNDATION = "in_foundation"
    STATUS_LOOKING_FOR_PEOPLE = "looking_for_people"
    STATUS_IDLE = "idle"
    STATUS_CHOICES = (
        (STATUS_ACTIVE, _("active")),
        (STATUS_IN_FOUNDATION, _("in foundation")),
        (STATUS_LOOKING_FOR_PEOPLE, _("looking for people")),
        (STATUS_IDLE, _("idle")),
    )

    status = models.CharField(
        _("Status"), max_length=50, default=STATUS_ACTIVE, choices=STATUS_CHOICES
    )
    founding_date = models.DateField(_("Founding date"), blank=True, null=True)

    email = models.EmailField(null=True, blank=True)
    pgp_key_id = models.CharField(null=True, blank=True, max_length=250)
    external_url = models.URLField(null=True, blank=True)
    phone = models.CharField(max_length=50, default="", blank=True)

    state = models.CharField(
        max_length=50, choices=LOCAL_GROUP_STATE_CHOICES, null=True, blank=True
    )
    location = models.CharField(
        max_length=255,
        blank=True,
        help_text=_(
            "Some city or address, like you would enter in GMaps or OpenStreetMap, "
            'e.g. "Berlin", "Somestreet 84, 12345 Samplecity".'
        ),
    )
    facebook = models.URLField(null=True, blank=True, help_text=_("Facebook page URL"))
    instagram = models.URLField(
        null=True, blank=True, help_text=_("Instagram page URL")
    )
    twitter = models.URLField(null=True, blank=True, help_text=_("Twitter page URL"))
    youtube = models.URLField(
        null=True, blank=True, help_text=_("YouTube channel or user account URL")
    )

    panels = [
        FieldPanel("name", classname="full"),
        FieldPanel("area_description"),
        MultiFieldPanel(
            [FieldPanel("status"), FieldPanel("founding_date")], heading=_("Status")
        ),
        MultiFieldPanel(
            [
                FieldPanel("email"),
                FieldPanel("pgp_key_id"),
                FieldPanel("phone"),
                FieldPanel("external_url"),
            ],
            heading=_("Contact"),
        ),
        MultiFieldPanel(
            [FieldPanel("state"), FieldPanel("location")], heading=_("Location")
        ),
        MultiFieldPanel(
            [
                FieldPanel("facebook"),
                FieldPanel("youtube"),
                FieldPanel("twitter"),
                FieldPanel("instagram"),
            ],
            heading=_("Social media"),
        ),
    ]

    objects = LocalGroupManager()

    class Meta:
        verbose_name = _("Local group")
        verbose_name_plural = _("Local groups")
        ordering = ("name",)

    @property
    def xr_name(self):
        return "XR %s" % self.name

    @property
    def first_letter(self):
        return self.name[0]

    @property
    def is_active(self):
        return self.status == self.STATUS_ACTIVE

    @property
    def active_localgrouppage(self):
        if (
            hasattr(self, "localgrouppage")
            and self.localgrouppage
            and self.localgrouppage.live
        ):
            return self.localgrouppage

    @property
    def active_eventgrouppage(self):
        if (
            hasattr(self, "eventgrouppage")
            and self.eventgrouppage
            and self.eventgrouppage.live
        ):
            return self.eventgrouppage

    @property
    def active_newsletterformpage(self):
        if (
            hasattr(self, "newsletterformpage")
            and self.newsletterformpage
            and self.newsletterformpage.live
            and self.newsletterformpage.sendy_list_id
        ):
            return self.newsletterformpage

    @property
    def upcoming_events(self):
        if not self.active_eventgrouppage:
            return []
        return self.active_eventgrouppage.upcoming_events

    @property
    def url(self):
        if self.external_url:
            return self.external_url
        if self.is_regional_group:
            return self.site.root_page.get_url()
        if self.active_localgrouppage:
            return self.localgrouppage.get_url()
        return None

    @property
    def full_url(self):
        if self.external_url:
            return self.external_url
        if self.is_regional_group:
            return self.site.root_page.get_full_url()
        if self.active_localgrouppage:
            return unquote(self.localgrouppage.get_full_url())
        return None

    @property
    def has_any_social_media_urls(self):
        return any([self.facebook, self.twitter, self.youtube, self.instagram])

    @property
    def newly_founded(self):
        if not self.founding_date:
            return None
        return self.founding_date + datetime.timedelta(90) < datetime.date.today()

    @property
    def founding_planned(self):
        if not self.founding_date:
            return None
        return self.founding_date > datetime.date.today()

    @property
    def is_looking_for_people(self):
        return self.status == self.STATUS_LOOKING_FOR_PEOPLE

    @property
    def is_in_foundation(self):
        return self.status == self.STATUS_IN_FOUNDATION

    @transaction.atomic
    def save(self, *args, **kwargs):
        is_new = self.id is None
        name_has_changed = self.old_name != self.name

        if is_new:
            from .signals import local_group_create

            local_group_create.send(sender=self.__class__, instance=self)
        elif name_has_changed:
            from .signals import local_group_name_change

            local_group_name_change.send(sender=self.__class__, instance=self)

        self.old_name = self.name

        if not hasattr(self, "site") or not self.site:
            self.site = get_site()

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


register_snippet(LocalGroup)


class LocalGroupListPage(XrPage):
    template = "xr_pages/pages/local_group_list.html"
    content = StreamField(ContentBlock, blank=True)
    group = models.OneToOneField(LocalGroup, editable=False, on_delete=models.PROTECT)

    content_panels = XrPage.content_panels + [StreamFieldPanel("content")]

    parent_page_types = []
    is_creatable = False

    class Meta:
        verbose_name = _("Local Group List Page")
        verbose_name_plural = _("Local Group List Pages")

    def save(self, *args, **kwargs):
        if not hasattr(self, "group") or self.group is None:
            self.group = self.get_parent().specific.group

        super().save(*args, **kwargs)


class LocalGroupPage(XrPage):
    template = "xr_pages/pages/local_group.html"
    content = StreamField(ContentBlock, blank=True)
    group = models.OneToOneField(LocalGroup, on_delete=models.PROTECT)

    content_panels = XrPage.content_panels + [
        SnippetChooserPanel("group"),
        StreamFieldPanel("content"),
    ]

    parent_page_types = ["LocalGroupListPage"]

    class Meta:
        verbose_name = _("Local Group Page")
        verbose_name_plural = _("Local Group Pages")

    @property
    def name(self):
        return self.group.name

    @property
    def xr_name(self):
        return "XR %s" % self.group.name

    @property
    def email(self):
        return self.group.email

    @property
    def state(self):
        return self.group.state

    @property
    def event_group(self):
        if hasattr(self.group, "eventgrouppage"):
            return self.group.eventgrouppage
        return None

    @property
    def is_regional_group(self):
        return self.group.is_regional_group


class LocalGroupSubPage(XrPage):
    template = "xr_pages/pages/local_group_sub.html"
    content = StreamField(ContentBlock, blank=True)
    group = models.ForeignKey(
        LocalGroup, on_delete=models.PROTECT, editable=False, related_name="+"
    )

    content_panels = XrPage.content_panels + [StreamFieldPanel("content")]

    parent_page_types = ["LocalGroupPage", "LocalGroupSubPage"]

    class Meta:
        verbose_name = _("Local Group Content Page")
        verbose_name_plural = _("Local Group Content Pages")

    def save(self, *args, **kwargs):
        if not hasattr(self, "group") or self.group is None:
            self.group = self.get_parent().specific.group

        super().save(*args, **kwargs)
