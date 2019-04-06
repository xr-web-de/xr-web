from django.utils.translation import ugettext as _
from wagtail.core import blocks

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


# Alignment choices
ALIGN_FULL_CONTENT = "full_content"
ALIGN_CENTER = "center"
ALIGN_LEFT = "left"
ALIGN_RIGHT = "right"
ALIGN_FULL_PAGE = "full_page"
ALIGN_CHOICES = (
    (ALIGN_CENTER, _("Center")),
    (ALIGN_FULL_CONTENT, _("Full content")),
    (ALIGN_LEFT, _("Left")),
    (ALIGN_RIGHT, _("Right")),
    (ALIGN_FULL_PAGE, _("Full page")),
)


# RichText defaults
simple_rich_text_features = [
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


# Block Mixins
# ------------------


class AlignmentMixin(blocks.StructBlock):
    align = blocks.ChoiceBlock(
        choices=ALIGN_CHOICES,
        default=ALIGN_FULL_CONTENT,
        help_text=_("Choose the alignment of the block."),
    )


# Common Block Fields


class AlignmentBlock(blocks.ChoiceBlock):
    choices = (ALIGN_CHOICES,)
    default = (ALIGN_FULL_CONTENT,)
    help_text = (_("Choose the alignment of the block."),)


alignment_block_kwargs = {
    "choices": ALIGN_CHOICES,
    "default": ALIGN_FULL_CONTENT,
    "help_text": _("Choose the alignment of the block."),
}


heading_block_kwargs = {
    "required": False,
    "help_text": _(
        "An optional heading, which is displayed above the block's content."
    ),
}


caption_block_kwargs = {
    "required": False,
    "help_text": _(
        "An optional caption, which is displayed below the block's content."
    ),
}

description_block_kwargs = {
    "required": False,
    "help_text": _(
        "An optional description, which is displayed below the block's caption"
    ),
}
