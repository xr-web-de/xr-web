from django.conf import settings
from django.utils.translation import ugettext as _
from wagtail.core import blocks
from wagtail.embeds.blocks import EmbedBlock
from wagtail.images.blocks import ImageChooserBlock


from xr_wagtail.block_utils import (
    heading_block_kwargs,
    simple_rich_text_features,
    caption_block_kwargs,
    description_block_kwargs,
    COLOR_CHOICES,
    COLOR_XR_WARM_YELLOW,
    COLOR_XR_GREEN,
    AlignmentMixin,
    CollapsibleFieldsMixin,
    COLOR_XR_BLACK,
    XrStructValue,
    ALIGN_CENTER,
    ALIGN_LEFT,
    COLOR_XR_TRANSPARENT,
    BG_COLOR_CHOICES,
)
from xr_newsletter.blocks import EmailFormBlock


# Blocks
# ---------
#
# Wrapping all inner blocks with StructBlocks seems to be good practice.
# This allows to append additional information later.


class TextBlock(CollapsibleFieldsMixin, blocks.StructBlock):
    text = blocks.RichTextBlock(
        features=simple_rich_text_features,
        help_text=_(
            "Simple richtext with basic formatting. "
            "Use links in order to connect related pages frequently. "
            "Ordered lists are rendered with big numbers."
            "For images and videos use the image and video blocks."
        ),
    )
    fields = ["heading", "text"]

    class Meta:
        icon = "pilcrow"
        template = "xr_pages/blocks/text.html"


class TitleBlock(CollapsibleFieldsMixin, blocks.StructBlock):
    title = blocks.CharBlock()
    font_color = blocks.ChoiceBlock(choices=COLOR_CHOICES, default=COLOR_XR_BLACK)
    ALIGN_CHOICES = ((ALIGN_CENTER, _("Center")), (ALIGN_LEFT, _("Left")))
    align = blocks.ChoiceBlock(
        choices=ALIGN_CHOICES,
        default=ALIGN_LEFT,
        help_text=_("Choose the alignment of the block."),
    )

    fields = ["title", {"label": _("Appearance"), "fields": ["align", "font_color"]}]

    class Meta:
        icon = "title"
        template = "xr_pages/blocks/title.html"


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
        value_class = XrStructValue


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
    keep_aspect_ratio = blocks.BooleanBlock(
        required=False,
        default=False,
        help_text=_(
            "If set, the image will not be cropped. "
            "Otherwise the image will be cropped to fill 16:9."
        ),
    )
    background_color = blocks.ChoiceBlock(
        choices=BG_COLOR_CHOICES, default=COLOR_XR_TRANSPARENT
    )
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
            "fields": [
                "align",
                "alternative_title",
                "keep_aspect_ratio",
                "attribution",
                "background_color",
            ],
        },
    ]

    class Meta:
        icon = "image"
        template = "xr_pages/blocks/image.html"
        value_class = XrStructValue


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
    font_color = blocks.ChoiceBlock(choices=COLOR_CHOICES, default=COLOR_XR_WARM_YELLOW)
    background_color = blocks.ChoiceBlock(
        choices=BG_COLOR_CHOICES, default=COLOR_XR_GREEN
    )
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
        value_class = XrStructValue


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
        "page",
        {"label": _("Card"), "fields": ["heading", "align", "caption", "description"]},
    ]

    class Meta:
        icon = "link"
        template = "xr_pages/blocks/teaser.html"
        value_class = XrStructValue


class UmapBlock(CollapsibleFieldsMixin, blocks.StructBlock):
    heading = blocks.CharBlock(**heading_block_kwargs)
    umap_url = blocks.ChoiceBlock(choices=settings.UMAP_URLS)
    caption = blocks.CharBlock(**caption_block_kwargs)
    description = blocks.TextBlock(**description_block_kwargs)

    fields = [
        "heading",
        "umap_url",
        {"label": _("Card"), "fields": ["caption", "description"]},
        {"label": _("Settings"), "fields": ["align"]},
    ]

    class Meta:
        icon = "site"
        template = "xr_pages/blocks/umap.html"
        value_class = XrStructValue


class GridBlock(CollapsibleFieldsMixin, blocks.StructBlock):
    heading = blocks.CharBlock(**heading_block_kwargs)
    items = blocks.StreamBlock(
        [
            ("teaser", TeaserBlock()),
            ("image", ImageBlock()),
            ("video", VideoBlock()),
            ("slogan", SloganBlock()),
        ]
    )
    COLUMN_CHOICES = ((2, _("2")), (3, _("3")), (4, _("4")))
    columns = blocks.ChoiceBlock(choices=COLUMN_CHOICES, default=3)
    font_color = blocks.ChoiceBlock(choices=COLOR_CHOICES, default=COLOR_XR_BLACK)
    background_color = blocks.ChoiceBlock(
        choices=BG_COLOR_CHOICES, default=COLOR_XR_TRANSPARENT
    )

    fields = [
        "heading",
        "columns",
        "items",
        {"label": _("Settings"), "fields": ["align", "font_color", "background_color"]},
    ]

    class Meta:
        icon = "grip"
        template = "xr_pages/blocks/grid.html"


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


class AlignedUmapBlock(AlignmentMixin, UmapBlock):
    pass


# Page content StreamField
class ContentBlock(blocks.StreamBlock):
    title = TitleBlock()
    text = TextBlock()
    image = AlignedImageBlock()
    teaser = AlignedTeaserBlock()
    video = AlignedVideoBlock()
    slogan = AlignedSloganBlock()
    form = EmailFormBlock()
    grid = GridBlock()
    umap = AlignedUmapBlock()
    # carousel = AlignedCarouselBlock()

    class Meta:
        template = "xr_pages/blocks/content.html"
