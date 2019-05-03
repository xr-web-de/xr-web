from django.utils.translation import ugettext as _
from wagtail.core import blocks
from wagtail.embeds.blocks import EmbedBlock
from wagtail.images.blocks import ImageChooserBlock


from xr_web.block_utils import (
    heading_block_kwargs,
    simple_rich_text_features,
    caption_block_kwargs,
    description_block_kwargs,
    COLOR_CHOICES,
    COLOR_XR_YELLOW,
    COLOR_XR_GREEN,
    AlignmentMixin,
    CollapsibleFieldsMixin,
)
from xr_newsletter.blocks import EmailFormBlock


# Blocks
# ---------
#
# Wrapping all inner blocks with StructBlocks seems to be good practice.
# This allows to append additional information later.


class TextBlock(CollapsibleFieldsMixin, blocks.StructBlock):
    heading = blocks.CharBlock(**heading_block_kwargs)
    text = blocks.RichTextBlock(
        features=simple_rich_text_features,
        help_text=_(
            "Simple richtext with basic formatting. "
            "Use links in order to connect related pages frequently. "
            "Ordered lists are rendered with big numbers."
            "For images and videos use the image and video blocks."
        ),
    )
    fields = [
        "heading",
        "text",
        # {
        #     "label": _("Settings"),
        #     "fields": [
        #         "align",
        #     ],
        # },
    ]

    class Meta:
        icon = "pilcrow"
        template = "xr_pages/blocks/text.html"


class LinkBlock(blocks.StructBlock):
    internal_link = blocks.PageChooserBlock(
        required=False,
        help_text=_('Link to an internal page. Is overwritten by "external link".'),
    )
    external_link = blocks.URLBlock(
        required=False,
        help_text=_(
            'Link to an external page (https://...). Overwrites "internal link".'
        ),
    )

    class Meta:
        icon = "link"
        template = "xr_pages/blocks/link.html"


class VideoBlock(CollapsibleFieldsMixin, blocks.StructBlock):
    heading = blocks.CharBlock(**heading_block_kwargs)
    video = EmbedBlock()
    caption = blocks.CharBlock(**caption_block_kwargs)
    description = blocks.TextBlock(**description_block_kwargs)

    fields = [
        "heading",
        "video",
        {"label": _("Card"), "fields": ["caption", "description"]},
        {"label": _("Settings"), "fields": ["align"]},
    ]

    class Meta:
        icon = "media"
        template = "xr_pages/blocks/video.html"


class ImageBlock(CollapsibleFieldsMixin, blocks.StructBlock):
    heading = blocks.CharBlock(**heading_block_kwargs)
    image = ImageChooserBlock()
    alternative_title = blocks.CharBlock(
        required=False,
        help_text=_(
            "An optional alternative title, which is displayed on hover. "
            "If not given, the image's title attribute will be used instead."
        ),
    )
    background_color = blocks.ChoiceBlock(choices=COLOR_CHOICES, default=COLOR_XR_GREEN)
    attribution = blocks.CharBlock(
        required=False,
        help_text=_(
            "An optional copyright or attribution text, which is displayed at "
            "the bottom right of the image."
        ),
    )
    caption = blocks.CharBlock(**caption_block_kwargs)
    description = blocks.TextBlock(**description_block_kwargs)

    link = LinkBlock(required=False)

    fields = [
        "heading",
        "image",
        {"label": _("Card"), "fields": ["caption", "description", "link"]},
        {
            "label": _("Settings"),
            "fields": ["align", "alternative_title", "attribution", "background_color"],
        },
    ]

    class Meta:
        icon = "image"
        template = "xr_pages/blocks/image.html"


class SloganBlock(CollapsibleFieldsMixin, blocks.StructBlock):
    heading = blocks.CharBlock(**heading_block_kwargs)
    text = blocks.TextBlock(
        required=False,
        rows=1,
        help_text=_("The text is displayed centered and linebreaks will be preserved."),
    )
    font_size = blocks.IntegerBlock(
        default=40,
        help_text=_(
            "Adjust the font size to fit your needs. Use the preview feature to see "
            "how big the font will be rendered."
        ),
    )
    font_color = blocks.ChoiceBlock(choices=COLOR_CHOICES, default=COLOR_XR_YELLOW)
    background_color = blocks.ChoiceBlock(choices=COLOR_CHOICES, default=COLOR_XR_GREEN)
    background_image = ImageChooserBlock(required=False)
    caption = blocks.CharBlock(**caption_block_kwargs)
    description = blocks.TextBlock(**description_block_kwargs)
    link = LinkBlock()

    fields = [
        "heading",
        "text",
        {"label": _("Card"), "fields": ["caption", "description", "link"]},
        {
            "label": _("Settings"),
            "fields": [
                "align",
                "font_size",
                "font_color",
                "background_color",
                "background_image",
            ],
        },
    ]

    class Meta:
        icon = "openquote"
        template = "xr_pages/blocks/slogan.html"


class TeaserBlock(CollapsibleFieldsMixin, blocks.StructBlock):
    heading = blocks.CharBlock(**heading_block_kwargs)
    page = blocks.PageChooserBlock()
    caption = blocks.CharBlock(
        required=False,
        help_text=_(
            "An optional caption, which is displayed below the block's content. "
            "Overwrites the page title of the linked page."
        ),
    )
    description = blocks.TextBlock(
        required=False,
        help_text=_(
            "An optional description, which is displayed below the block's caption. "
            "Overwrites the page description of the linked page."
        ),
    )

    fields = [
        "heading",
        "page",
        {"label": _("Card"), "fields": ["heading", "align", "caption", "description"]},
    ]

    class Meta:
        icon = "link"
        template = "xr_pages/blocks/teaser.html"


class CarouselBlock(blocks.StructBlock):
    items = blocks.StreamBlock(
        [("image", ImageBlock()), ("video", VideoBlock()), ("slogan", SloganBlock())]
    )


# Alignable variations of the above blocks for the content StreamField
class AlignedImageBlock(AlignmentMixin, ImageBlock):
    pass


class AlignedVideoBlock(AlignmentMixin, VideoBlock):
    pass


class AlignedSloganBlock(AlignmentMixin, SloganBlock):
    pass


class AlignedTeaserBlock(AlignmentMixin, TeaserBlock):
    pass


class AlignedCarouselBlock(AlignmentMixin, CarouselBlock):
    pass


# Page content StreamField
class ContentBlock(blocks.StreamBlock):
    text = TextBlock()
    image = AlignedImageBlock()
    teaser = AlignedTeaserBlock()
    video = AlignedVideoBlock()
    slogan = AlignedSloganBlock()
    form = EmailFormBlock()
    # carousel = AlignedCarouselBlock()

    class Meta:
        template = "xr_pages/blocks/content.html"
