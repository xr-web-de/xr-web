from wagtail.core import blocks


class EmailFormBlock(blocks.StructBlock):
    form_page = blocks.PageChooserBlock(
        ["xr_newsletter.EmailFormPage", "xr_newsletter.NewsletterFormPage"]
    )

    class Meta:
        icon = "form"
        template = "xr_newsletter/blocks/email_form.html"

    @property
    def form(self):
        return self.form_page.get_form()

    @property
    def action(self):
        return self.form_page.get_url()

    @property
    def form_id(self):
        return "{}_{}".format("email_form_block", self.creation_counter)
