from django.contrib.auth.models import Group
from django.db import models, transaction
from django.utils.translation import ugettext as _
from wagtail.admin.edit_handlers import StreamFieldPanel
from wagtail.core.fields import StreamField
from wagtail.core.models import Page, Collection
from wagtail.snippets.edit_handlers import SnippetChooserPanel
from wagtail.snippets.models import register_snippet

from .blocks import ContentBlock


class HomePage(Page):
    template = "xr_pages/pages/home.html"
    content = StreamField(ContentBlock, blank=True)
    group = models.OneToOneField("LocalGroup", editable=False, on_delete=models.PROTECT)

    content_panels = Page.content_panels + [StreamFieldPanel("content")]

    parent_page_types = []
    is_creatable = False


class HomeSubPage(Page):
    template = "xr_pages/pages/home_sub.html"
    content = StreamField(ContentBlock, blank=True)
    group = models.ForeignKey("LocalGroup", editable=False, on_delete=models.PROTECT)

    content_panels = Page.content_panels + [StreamFieldPanel("content")]

    parent_page_types = ["HomePage"]

    def save(self, *args, **kwargs):
        if not hasattr(self, "group") or self.group is None:
            self.group = self.get_parent().specific.group

        super().save(*args, **kwargs)


class LocalGroup(models.Model):
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
    email = models.EmailField(null=True, blank=True)
    url = models.URLField(null=True, blank=True)
    phone = models.CharField(max_length=50, default="", blank=True)
    # TODO: move state choices to settings
    GERMANY_STATE_CHOICES = (
        ("BW", "Baden-Württemberg"),
        ("BY", "Bayern"),
        ("BE", "Berlin"),
        ("BB", "Brandenburg"),
        ("HB", "Bremen"),
        ("HH", "Hamburg"),
        ("HE", "Hessen"),
        ("MV", "Mecklenburg-Vorpommern"),
        ("NI", "Niedersachsen"),
        ("NW", "Nordrhein-Westfalen"),
        ("RP", "Rheinland-Pfalz"),
        ("SL", "Saarland"),
        ("SN", "Sachsen"),
        ("ST", "Sachsen-Anhalt"),
        ("SH", "Schleswig-Holstein"),
        ("TH", "Thüringen"),
    )
    state = models.CharField(
        max_length=50, choices=GERMANY_STATE_CHOICES, null=True, blank=True
    )
    location = models.CharField(
        max_length=255,
        blank=True,
        help_text=_(
            "Some city or address, like you would enter in GMaps or OpenStreetMap, "
            'e.g. "Berlin", "Somestreet 84, 12345 Samplecity".'
        ),
    )

    class Meta:
        verbose_name = _("Group")
        verbose_name_plural = _("Groups")

    @property
    def xr_name(self):
        return "XR %s" % self.name

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

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


register_snippet(LocalGroup)


class LocalGroupListPage(Page):
    template = "xr_pages/pages/local_group_list.html"
    content = StreamField(ContentBlock, blank=True)

    content_panels = Page.content_panels + [StreamFieldPanel("content")]

    parent_page_types = []
    is_creatable = False

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        context["local_groups"] = (
            LocalGroupPage.objects.child_of(self).live().order_by("-title")
        )
        return context


class LocalGroupPage(Page):
    template = "xr_pages/pages/local_group.html"
    content = StreamField(ContentBlock, blank=True)
    group = models.OneToOneField(LocalGroup, on_delete=models.PROTECT)

    content_panels = Page.content_panels + [
        SnippetChooserPanel("group"),
        StreamFieldPanel("content"),
    ]

    parent_page_types = ["LocalGroupListPage"]

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

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if self.group and not self.group.url:
            self.group.url = self.get_full_url()
            self.group.save()


class LocalGroupSubPage(Page):
    template = "xr_pages/pages/local_group_sub.html"
    content = StreamField(ContentBlock, blank=True)
    group = models.ForeignKey(
        LocalGroup, on_delete=models.PROTECT, editable=False, related_name="+"
    )

    content_panels = Page.content_panels + [StreamFieldPanel("content")]

    parent_page_types = ["LocalGroupPage"]

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        context["parent_page"] = self.get_parent()
        context["local_group_page"] = self.get_parent()
        return context

    def save(self, *args, **kwargs):
        if not hasattr(self, "group") or self.group is None:
            self.group = self.get_parent().specific.group

        super().save(*args, **kwargs)
