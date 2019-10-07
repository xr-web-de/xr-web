from django.core.validators import RegexValidator
from django.utils.translation import ugettext as _
from wagtail.core import blocks
from wagtail.embeds.blocks import EmbedBlock

from xr_wagtail.block_utils import (
    CollapsibleFieldsMixin,
    heading_block_kwargs,
    caption_block_kwargs,
    description_block_kwargs,
    XrStructValue,
)


css_length_validator = RegexValidator(
    r"^(\d+\.)?\d+(px|em|%)$",
    message=_(
        "Please enter a valid floating number with one of these units: 'px', 'em', '%'."
    ),
)


class GdprEmbedBlock(CollapsibleFieldsMixin, blocks.StructBlock):
    heading = blocks.CharBlock(**heading_block_kwargs)
    embed = EmbedBlock()
    caption = blocks.CharBlock(**caption_block_kwargs)
    description = blocks.TextBlock(**description_block_kwargs)
    show_gdpr_message = blocks.BooleanBlock(default=True, required=False)
    width = blocks.CharBlock(
        required=False, default="", validators=[css_length_validator]
    )
    height = blocks.CharBlock(
        required=False, default="", validators=[css_length_validator]
    )

    fields = [
        "heading",
        "embed",
        "show_gdpr_message",
        {"label": _("Card"), "fields": ["caption", "description"]},
        {"label": _("Settings"), "fields": ["align", "width", "height"]},
    ]

    class Meta:
        icon = "media"
        template = "xr_embeds/blocks/gdpr_embed.html"
        value_class = XrStructValue
