from wagtail.core import blocks


from xr_pages.block_utils import (
    heading_block_kwargs,
    caption_block_kwargs,
    description_block_kwargs,
    COLOR_CHOICES,
    COLOR_XR_BLACK,
    COLOR_XR_WHITE,
)


class EmailFormBlock(blocks.StructBlock):
    heading = blocks.CharBlock(**heading_block_kwargs)
    form_page = blocks.PageChooserBlock(
        ["xr_newsletter.EmailFormPage", "xr_newsletter.NewsletterFormPage"]
    )
    font_color = blocks.ChoiceBlock(choices=COLOR_CHOICES, default=COLOR_XR_BLACK)
    background_color = blocks.ChoiceBlock(choices=COLOR_CHOICES, default=COLOR_XR_WHITE)
    caption = blocks.CharBlock(**caption_block_kwargs)
    description = blocks.TextBlock(**description_block_kwargs)

    class Meta:
        icon = "form"
        template = "xr_newsletter/blocks/email_form.html"
