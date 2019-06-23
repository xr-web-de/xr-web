from django.db import models
from django.utils.translation import ugettext as _
from wagtail.admin.edit_handlers import StreamFieldPanel, FieldPanel, MultiFieldPanel
from wagtail.core.fields import StreamField

from xr_pages.blocks import ContentBlock
from xr_pages.models import (
    XrPage,
    HomePage,
    LocalGroupPage,
    HomeSubPage,
    LocalGroupSubPage,
)


class BlogEntryPage(XrPage):
    template = "xr_blog/pages/blog_entry.html"
    group = models.ForeignKey(
        "xr_pages.LocalGroup",
        editable=False,
        on_delete=models.PROTECT,
        related_name="blog_entries",
    )
    date = models.DateField(_("Post date"))
    author = models.CharField(max_length=200)
    content = StreamField(
        ContentBlock,
        blank=True,
        help_text=_("The content is only visible on the detail page."),
    )

    # Panels (Editor interface)
    content_panels = [
        MultiFieldPanel(
            [
                FieldPanel("title", classname="title"),
                # FieldPanel("show_page_title", classname=""),  # without "show_page_title"
            ],
            heading=_("Title"),
        ),
        FieldPanel("date"),
        FieldPanel("author"),
        StreamFieldPanel("content"),
    ]

    parent_page_types = ["BlogListPage"]

    class Meta:
        verbose_name = _("Blog Entry Page")
        verbose_name_plural = _("Blog Entry Pages")

    def save(self, *args, **kwargs):
        if not hasattr(self, "group") or not self.group:
            self.group = self.get_parent().specific.group

        super().save(*args, **kwargs)


class BlogListPage(XrPage):
    template = "xr_blog/pages/blog_list.html"
    group = models.OneToOneField(
        "xr_pages.LocalGroup", editable=False, on_delete=models.PROTECT
    )
    content = StreamField(
        ContentBlock,
        blank=True,
        help_text=_("The content is only visible on the detail page."),
    )

    parent_page_types = [HomePage, HomeSubPage, LocalGroupPage, LocalGroupSubPage]

    content_panels = XrPage.content_panels + [StreamFieldPanel("content")]

    class Meta:
        verbose_name = _("Blog List Page")
        verbose_name_plural = _("Blog List Pages")

    def save(self, *args, **kwargs):
        if not hasattr(self, "group") or not self.group:
            self.group = self.get_parent().specific.group

        super().save(*args, **kwargs)

    def entries(self):
        return BlogEntryPage.objects.child_of(self).live().order_by("-date")
