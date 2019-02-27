from wagtail.admin.edit_handlers import StreamFieldPanel
from wagtail.core.fields import StreamField
from wagtail.core.models import Page

from xr_pages.blocks import ContentBlock


class StandardPage(Page):
    template = "xr_pages/pages/standard.html"
    content = StreamField(ContentBlock)

    content_panels = Page.content_panels + [StreamFieldPanel("content")]
