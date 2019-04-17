import json

from django.contrib import messages
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models

from django.shortcuts import render
from django.utils.text import slugify
from django.utils.translation import ugettext as _
from modelcluster.fields import ParentalKey
from unidecode import unidecode
from wagtail.admin.edit_handlers import (
    FieldRowPanel,
    FieldPanel,
    MultiFieldPanel,
    InlinePanel,
    StreamFieldPanel,
)
from wagtail.contrib.forms.models import AbstractEmailForm, AbstractFormField
from wagtail.core.fields import StreamField
from wagtail.core.models import Page, Orderable

from xr_newsletter.forms import WagtailAdminNewsletterFormPageForm
from xr_newsletter.services import sendy_api
from xr_pages.blocks import ContentBlock
from xr_web.edit_handlers import FieldCollapsiblePanel
from xr_pages.models import LocalGroup, HomePage, LocalGroupPage


class EmailFormField(AbstractFormField):
    page = ParentalKey(
        "EmailFormPage", on_delete=models.CASCADE, related_name="form_fields"
    )

    panels = [
        FieldRowPanel((FieldPanel("label"),)),
        FieldCollapsiblePanel(
            [
                FieldPanel("help_text"),
                FieldRowPanel(
                    (
                        FieldPanel("field_type", classname="formbuilder-type"),
                        FieldPanel("required"),
                    )
                ),
                FieldRowPanel(
                    (
                        FieldPanel("choices", classname="formbuilder-choices"),
                        FieldPanel("default_value", classname="formbuilder-default"),
                    )
                ),
            ],
            heading=_("Settings"),
        ),
    ]

    class Meta:
        ordering = ["sort_order"]

    def __str__(self):
        return self.label


class AbstractEmailFormPage(AbstractEmailForm):
    content = StreamField(ContentBlock, blank=True)
    thank_you_text = StreamField(ContentBlock, blank=True)

    content_panels = AbstractEmailForm.content_panels + [
        StreamFieldPanel("content"),
        InlinePanel("form_fields", label=_("Form fields")),
        StreamFieldPanel("thank_you_text"),
    ]

    settings_panels = Page.settings_panels + [
        MultiFieldPanel(
            [
                FieldRowPanel(
                    [
                        FieldPanel("from_address", classname="col6"),
                        FieldPanel("to_address", classname="col6"),
                    ]
                ),
                FieldPanel("subject"),
            ],
            _("Send email on submit"),
        )
    ]

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if not hasattr(self, "group") or self.group is None:
            self.group = self.get_parent().specific.group

        super().save(*args, **kwargs)


class EmailFormPage(AbstractEmailFormPage):
    template = "xr_newsletter/pages/email_form.html"
    landing_page_template = "xr_newsletter/pages/email_form_thank_you.html"
    group = models.ForeignKey(LocalGroup, editable=False, on_delete=models.PROTECT)

    parent_page_types = [HomePage, LocalGroupPage]

    def process_form_submission(self, form):
        submission = self.get_submission_class()(
            form_data=json.dumps(form.cleaned_data, cls=DjangoJSONEncoder), page=self
        )
        if self.to_address:
            self.send_mail(form)
        return submission

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        context.update({"action": self.url, "form_id": "email_form"})
        return context


class NewsletterFormField(AbstractFormField):
    page = ParentalKey(
        "NewsletterFormPage", on_delete=models.CASCADE, related_name="form_fields"
    )

    name = models.SlugField(
        verbose_name=_("name"),
        max_length=255,
        help_text=_("A unique name for the form field"),
    )

    panels = [
        FieldRowPanel((FieldPanel("label"), FieldPanel("name"))),
        FieldCollapsiblePanel(
            [
                FieldPanel("help_text"),
                FieldRowPanel(
                    (
                        FieldPanel("field_type", classname="formbuilder-type"),
                        FieldPanel("required"),
                    )
                ),
                FieldRowPanel(
                    (
                        FieldPanel("choices", classname="formbuilder-choices"),
                        FieldPanel("default_value", classname="formbuilder-default"),
                    )
                ),
            ],
            heading=_("Settings"),
        ),
    ]

    class Meta:
        unique_together = ("page", "name")
        ordering = ["sort_order"]

    @property
    def clean_name(self):
        # unidecode will return an ascii string while slugify wants a
        # unicode string on the other hand, slugify returns a safe-string
        # which will be converted to a normal str
        return str(slugify(str(unidecode(self.name))))

    def __str__(self):
        return self.label


class NewsletterFormPage(AbstractEmailFormPage):
    template = "xr_newsletter/pages/newsletter_form.html"
    landing_page_template = "xr_newsletter/pages/newsletter_form_thank_you.html"
    group = models.OneToOneField(LocalGroup, editable=False, on_delete=models.PROTECT)
    sendy_list_id = models.CharField(max_length=254, null=True, blank=True)

    settings_panels = AbstractEmailFormPage.settings_panels + [
        MultiFieldPanel(
            [FieldPanel("sendy_list_id")],
            _("Subscribe to Sendy newsletter list on submit"),
        )
    ]

    parent_page_types = [LocalGroupPage]

    base_form_class = WagtailAdminNewsletterFormPageForm

    def serve(self, request, *args, **kwargs):
        if request.method == "POST":
            form = self.get_form(
                request.POST, request.FILES, page=self, user=request.user
            )

            if form.is_valid():
                form_submission = self.get_submission_class()(
                    form_data=json.dumps(form.cleaned_data, cls=DjangoJSONEncoder),
                    page=self,
                )
                if self.to_address:
                    self.send_mail(form)

                if self.sendy_list_id:
                    data = {
                        "email": form.cleaned_data.get("email", None),
                        "name": form.cleaned_data.get("name", None),
                        "gdpr": form.cleaned_data.get("gdpr", None),
                    }

                    sendy_response = sendy_api.subscribe(self.sendy_list_id, **data)

                    if sendy_response == "true" or int(sendy_response) == 1:
                        return self.render_landing_page(
                            request, form_submission, *args, **kwargs
                        )

                message = _(
                    "Sorry, there was an error talking to the Newsletter API. "
                    "Please try again later."
                )
                messages.error(request, message)
                # form = self.get_form(page=self, user=request.user)
        else:
            form = self.get_form(page=self, user=request.user)

        context = self.get_context(request)
        context["form"] = form

        return render(request, self.get_template(request), context)

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        context.update({"action": self.url, "form_id": "newsletter_form"})
        return context
