import json

from condensedinlinepanel.edit_handlers import CondensedInlinePanel
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models

# Create your models here.
from django.shortcuts import render
from django.utils.text import slugify
from django.utils.translation import ugettext as _
from modelcluster.fields import ParentalKey
from sendy.exceptions import SendyError
from unidecode import unidecode
from wagtail.admin.edit_handlers import FieldRowPanel, FieldPanel, MultiFieldPanel
from wagtail.contrib.forms.models import AbstractEmailForm, AbstractFormField
from wagtail.core.fields import StreamField
from wagtail.core.models import Page, Orderable

from xr_newsletter.services import sendy_api
from xr_pages.blocks import ContentBlock
from xr_pages.models import LocalGroup, HomePage, LocalGroupPage


class EmailFormField(AbstractFormField):
    page = ParentalKey(
        "EmailFormPage", on_delete=models.CASCADE, related_name="form_fields"
    )

    panels = [
        FieldRowPanel((FieldPanel("label"),)),
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
    ]


class AbstractEmailFormPage(AbstractEmailForm):
    content = StreamField(ContentBlock, blank=True)
    thank_you_text = StreamField(ContentBlock, blank=True)

    content_panels = AbstractEmailForm.content_panels + [
        FieldPanel("content", classname="full"),
        CondensedInlinePanel("form_fields", label=_("Form fields")),
        FieldPanel("thank_you_text", classname="full"),
    ]

    settings_panels = AbstractEmailForm.settings_panels + [
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
        if self.group is None:
            self.group = self.get_parent().group

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
    ]

    class Meta:
        unique_together = ("page", "name")

    @property
    def clean_name(self):
        # unidecode will return an ascii string while slugify wants a
        # unicode string on the other hand, slugify returns a safe-string
        # which will be converted to a normal str
        return str(slugify(str(unidecode(self.name))))


class NewsletterFormPage(AbstractEmailFormPage):
    template = "xr_newsletter/pages/newsletter_form.html"
    landing_page_template = "xr_newsletter/pages/newsletter_form_thank_you.html"
    group = models.OneToOneField(LocalGroup, editable=False, on_delete=models.PROTECT)
    sendy_list_id = models.CharField(max_length=254, null=True, blank=True)

    settings_panels = [
        MultiFieldPanel(
            [FieldPanel("sendy_list_id")],
            _("Subscribe to Sendy newsletter list on submit"),
        )
    ] + AbstractEmailFormPage.settings_panels

    parent_page_types = [LocalGroupPage]

    def get_form_parameters(self):
        form_parmas = super().get_form_parameters()

        form_fields = (
            [
                NewsletterFormField(
                    page=self,
                    label=_("Email"),
                    name="email",
                    field_type="email",
                    required=True,
                ),
                NewsletterFormField(
                    page=self,
                    label=_("Name"),
                    name="name",
                    field_type="singleline",
                    required=False,
                ),
                NewsletterFormField(
                    page=self,
                    label=_("I agree"),
                    name="gdpr",
                    field_type="checkbox",
                    required=True,
                    help_text=_(
                        "GDPR Permission: I give my consent to Extinction Rebellion to get "
                        "in touch with me using the information I have provided in this "
                        "form, for the purpose of news, updates, and rebellion"
                    ),
                ),
            ],
        )

        form_parmas.update({"initial": {"form_fields": form_fields}})

        return form_parmas

    def clean(self):
        super().clean()

        required_fields = ["email", "gdpr"]

        for field_name in required_fields:
            form_field_qs = self.form_fields.filter(name=field_name)

            if not form_field_qs.exists():
                raise ValidationError(
                    'A form field with the label "%s" is required, '
                    "in order to allow subscribing to the newsletter." % field_name
                )

            form_field = form_field_qs.first()

            if form_field.required is False:
                raise ValidationError(
                    'The "%s" form field must be set required, '
                    "in order to allow subscribing to the newsletter." % field_name
                )

        if not self.form_fields.filter(name="name").exists():
            raise ValidationError(
                'A form field with the label "name" or "Name" is required, '
                "in order to allow subscribing to the newsletter."
            )

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
                        "list_id": self.sendy_list_id,
                        "email": form.cleaned_data.get("email", None),
                        "name": form.cleaned_data.get("name", None),
                        "gdpr": form.cleaned_data.get("gdpr", None),
                    }

                    sendy_response = sendy_api.subscribe(**data)

                    if sendy_response == "true":
                        return self.render_landing_page(
                            request, form_submission, *args, **kwargs
                        )

                message = _(
                    "Sorry, there was an error talking to the Newsletter API. "
                    "Please try again later."
                )
                messages.error(request, message)
                form = self.get_form(page=self, user=request.user)
        else:
            form = self.get_form(page=self, user=request.user)

        context = self.get_context(request)
        context["form"] = form

        return render(request, self.get_template(request), context)

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        context.update({"action": self.url, "form_id": "newsletter_form"})
        return context
