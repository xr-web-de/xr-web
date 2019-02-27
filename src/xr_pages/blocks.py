from django.utils.translation import ugettext as _
from wagtail.core import blocks
from wagtail.embeds.blocks import EmbedBlock
from wagtail.images.blocks import ImageChooserBlock


# Theme color palette (python constants for css classes)
COLOR_XR_GREEN = "xr-green"
COLOR_XR_YELLOW = "xr-yellow"
COLOR_XR_LIGHT_BLUE = "xr-light-blue"
COLOR_XR_DARK_BLUE = "xr-dark-blue"
COLOR_XR_WHITE = "xr-white"
COLOR_XR_BLACK = "xr-black"
COLOR_CHOICES = (
    (COLOR_XR_GREEN, _("XR green")),
    (COLOR_XR_YELLOW, _("XR yellow")),
    (COLOR_XR_LIGHT_BLUE, _("XR light blue")),
    (COLOR_XR_DARK_BLUE, _("XR dark blue")),
    (COLOR_XR_WHITE, _("XR white")),
    (COLOR_XR_BLACK, _("XR black")),
)


# RichText defaults
simple_rich_text_features = [
    "h2",
    "h3",
    "h4",
    "bold",
    "italic",
    "ul",
    "ol",
    "hr",
    "link",
    "document-link",
]


# Blocks
# ---------
#
# Wrapping all inner blocks with StructBlocks seems to be good practice.
# This allows to append additional information later.
class TextBlock(blocks.StructBlock):
    text = blocks.RichTextBlock(features=simple_rich_text_features)

    class Meta:
        icon = "pilcrow"
        template = "xr_pages/blocks/text.html"


class LinkBlock(blocks.StructBlock):
    internal_link = blocks.PageChooserBlock(required=False)
    external_link = blocks.URLBlock(required=False)

    class Meta:
        icon = "link"
        template = "xr_pages/blocks/link.html"

    def has_link(self):
        if self.external_link or self.internal_link:
            return True
        return False


class VideoBlock(blocks.StructBlock):
    video = EmbedBlock()
    caption = blocks.CharBlock(required=False)

    class Meta:
        icon = "media"
        template = "xr_pages/blocks/video.html"


class ImageBlock(blocks.StructBlock):
    image = ImageChooserBlock()
    alternative_title = blocks.CharBlock(required=False)
    caption = blocks.CharBlock(required=False)
    attribution = blocks.CharBlock(required=False)
    link = LinkBlock(required=False)

    class Meta:
        icon = "image"
        template = "xr_pages/blocks/image.html"

    @property
    def get_title(self):
        if self.alternative_title:
            return self.alternative_title
        else:
            self.image.title


class MessageBlock(blocks.StructBlock):
    message = TextBlock()
    font_size_factor = blocks.FloatBlock(default=1)
    font_color = blocks.ChoiceBlock(choices=COLOR_CHOICES, default=COLOR_XR_YELLOW)
    background_color = blocks.ChoiceBlock(choices=COLOR_CHOICES, default=COLOR_XR_GREEN)
    background_image = ImageChooserBlock(required=False)
    link = LinkBlock()

    class Meta:
        icon = "openquote"
        template = "xr_pages/blocks/message.html"


class CarouselBlock(blocks.StructBlock):
    items = blocks.StreamBlock(
        [("image", ImageBlock()), ("video", VideoBlock()), ("message", MessageBlock())]
    )


# Alignment choices
ALIGN_FULL_CONTENT = "full_content"
ALIGN_LEFT = "left"
ALIGN_RIGHT = "right"
ALIGN_FULL_PAGE = "full_page"
ALIGN_CHOICES = (
    (ALIGN_FULL_CONTENT, _("Full content")),
    (ALIGN_LEFT, _("Left")),
    (ALIGN_RIGHT, _("Right")),
    (ALIGN_FULL_PAGE, _("Full page")),
)


class AlignmentMixin(blocks.StructBlock):
    align = blocks.ChoiceBlock(choices=ALIGN_CHOICES, default=ALIGN_FULL_CONTENT)


# Alignable variations of the above blocks for the content StreamField
class AlignedImageBlock(AlignmentMixin, ImageBlock):
    pass


class AlignedVideoBlock(AlignmentMixin, VideoBlock):
    pass


class AlignedMessageBlock(AlignmentMixin, MessageBlock):
    pass


class AlignedCarouselBlock(AlignmentMixin, CarouselBlock):
    pass


# Page content StreamField
class ContentBlock(blocks.StreamBlock):
    text = TextBlock()
    image = AlignedImageBlock()
    video = AlignedVideoBlock()
    message = AlignedMessageBlock()
    carousel = AlignedCarouselBlock()

    class Meta:
        template = "xr_pages/blocks/content.html"
