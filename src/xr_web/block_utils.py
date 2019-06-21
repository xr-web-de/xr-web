from collections import OrderedDict

from django.utils.translation import ugettext as _
from wagtail.core import blocks

# Theme color palette (python constants for css classes)
from wagtail.core.blocks import StructValue

COLOR_XR_TRANSPARENT = "xr-transparent"
COLOR_XR_GREEN = "xr-green"
COLOR_XR_BLACK = "xr-black"
COLOR_XR_LEMON = "xr-lemon"
COLOR_XR_LIGHT_BLUE = "xr-light-blue"
COLOR_XR_PINK = "xr-pink"
COLOR_XR_PURPLE = "xr-purple"
COLOR_XR_LIGHT_GREEN = "xr-light-green"
COLOR_XR_WARM_YELLOW = "xr-warm-yellow"
COLOR_XR_BRIGHT_PINK = "xr-bright-pink"
COLOR_XR_RED = "xr-red"
COLOR_XR_DARK_BLUE = "xr-dark-blue"
COLOR_XR_ANGRY = "xr-angry"
COLOR_XR_WHITE = "xr-white"
COLOR_XR_LIGHT_GREY = "xr-light-grey"
COLOR_XR_GREY = "xr-grey"
COLOR_XR_DARK_GREY = "xr-dark-grey"

COLOR_CHOICES = (
    (COLOR_XR_GREEN, _("Green")),
    (COLOR_XR_BLACK, _("Black")),
    (COLOR_XR_LEMON, _("Lemon")),
    (COLOR_XR_LIGHT_BLUE, _("Light blue")),
    (COLOR_XR_PINK, _("Pink")),
    (COLOR_XR_PURPLE, _("Purple")),
    (COLOR_XR_LIGHT_GREEN, _("Light green")),
    (COLOR_XR_WARM_YELLOW, _("Warm yellow")),
    (COLOR_XR_BRIGHT_PINK, _("Bright pink")),
    (COLOR_XR_RED, _("Red")),
    (COLOR_XR_DARK_BLUE, _("Dark blue")),
    (COLOR_XR_ANGRY, _("Angry")),
    (COLOR_XR_WHITE, _("White")),
    (COLOR_XR_LIGHT_GREY, _("Light grey")),
    (COLOR_XR_GREY, _("Grey")),
    (COLOR_XR_DARK_GREY, _("Dark grey")),
)

BG_COLOR_CHOICES = (COLOR_XR_TRANSPARENT, _("None / Transparent")) + COLOR_CHOICES

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


# Block Mixins
# ------------------


class XrStructValue(StructValue):
    def align(self):
        align = self.get("align")
        if not align:
            return "default"
        return align

    def get_link(self):
        link_block = self.get("link")
        if link_block:
            external_link = link_block.get("external_link")
            if external_link:
                return external_link

            internal_link = link_block.get("internal_link")
            if internal_link:
                return internal_link
        return ""


class AlignmentMixin(blocks.StructBlock):
    align = blocks.ChoiceBlock(
        choices=ALIGN_CHOICES,
        default=ALIGN_FULL_CONTENT,
        help_text=_("Choose the alignment of the block."),
    )


class CollapsibleFieldsMixin(blocks.StructBlock):
    def get_form_context(self, value, prefix="", errors=None):
        context = super().get_form_context(value, prefix=prefix, errors=errors)

        if self.fields:
            children = context.get("children", OrderedDict())
            fields = [
                children.get(field)
                for field in self.fields
                if isinstance(field, str) and field in children
            ]

            fieldsets = []
            for fieldset in [f for f in self.fields if isinstance(f, dict)]:
                fieldset = {
                    "label": fieldset["label"],
                    "fields": [
                        children.get(field)
                        for field in fieldset["fields"]
                        if isinstance(field, str) and field in children
                    ],
                }
                fieldsets.append(fieldset)

            context.update({"fields": fields, "fieldsets": fieldsets})
        return context

    class Meta:
        form_template = "xr_web/block_forms/collapsible_struct.html"


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
        "An optional description, which is displayed below the block's caption."
    ),
}
