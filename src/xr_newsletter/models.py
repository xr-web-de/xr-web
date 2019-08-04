import json
import re

import requests
from django.conf import settings
from django.contrib import messages
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models

from django.shortcuts import render, redirect
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
from wagtail.core.models import Page

from xr_newsletter.forms import (
    WagtailAdminMauticNewsletterFormPageForm,
    WagtailAdminGdprFormPageForm,
    PlaceholderFormBuilder,
)
from xr_newsletter.services import sendy_api
from xr_pages.blocks import ContentBlock
from xr_pages.services import get_home_page
from xr_web.edit_handlers import FieldCollapsiblePanel
from xr_pages.models import (
    LocalGroup,
    HomePage,
    LocalGroupPage,
    XrPage,
    HomeSubPage,
    LocalGroupSubPage,
)


class NamedAbstractFormField(AbstractFormField):
    name = models.CharField(
        verbose_name=_("name"),
        max_length=255,
        help_text=_("A unique name for the form field"),
        null=True,
        blank=True,
    )
    placeholder = models.CharField(
        verbose_name=_("placeholder"),
        max_length=255,
        help_text=_("The placeholder is displayed in grey, and disappears on focus."),
        default="",
        blank=True,
    )

    panels = [
        FieldRowPanel(
            (FieldPanel("label"), FieldPanel("name"), FieldPanel("required"))
        ),
        FieldCollapsiblePanel(
            [
                FieldRowPanel(
                    (
                        FieldPanel("field_type", classname="formbuilder-type"),
                        FieldPanel("choices", classname="formbuilder-choices"),
                    )
                ),
                FieldRowPanel(
                    (
                        FieldPanel("placeholder"),
                        FieldPanel("default_value", classname="formbuilder-default"),
                    )
                ),
                FieldPanel("help_text"),
            ],
            heading=_("Settings"),
        ),
    ]

    class Meta:
        unique_together = ("page", "name")
        ordering = ["sort_order"]
        abstract = True

    @property
    def clean_name(self):
        # unidecode will return an ascii string while slugify wants a
        # unicode string on the other hand, slugify returns a safe-string
        # which will be converted to a normal str
        if self.name:
            return str(slugify(str(unidecode(self.name))))
        return "field_{}".format(self.id)

    def __str__(self):
        return "{} ({})".format(self.label, self.name)


class EmailFormField(NamedAbstractFormField):
    page = ParentalKey(
        "EmailFormPage", on_delete=models.CASCADE, related_name="form_fields"
    )

    class Meta:
        unique_together = ("page", "name")
        ordering = ["sort_order"]


class AbstractEmailFormPage(AbstractEmailForm, XrPage):
    content = StreamField(ContentBlock, blank=True)
    group = models.ForeignKey(LocalGroup, editable=False, on_delete=models.PROTECT)

    form_builder = PlaceholderFormBuilder

    content_panels = AbstractEmailForm.content_panels + [
        StreamFieldPanel("content"),
        InlinePanel("form_fields", label=_("Form fields")),
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

    def get_landing_page(self, request=None):
        qs = ThankYouPage.objects.live().child_of(self)
        if qs.exists():
            return qs.first()

        if request:
            message = _("Thank you! Your form was submitted successfully.")
            messages.success(request, message)
        return get_home_page()

    def save(self, *args, **kwargs):
        if not hasattr(self, "group") or self.group is None:
            self.group = self.get_parent().specific.group

        super().save(*args, **kwargs)


class EmailFormPage(AbstractEmailFormPage):
    template = "xr_newsletter/pages/email_form.html"

    save_submission = models.BooleanField(default=False, blank=True)

    parent_page_types = [HomePage, LocalGroupPage, HomeSubPage, LocalGroupSubPage]

    base_form_class = WagtailAdminGdprFormPageForm

    settings_panels = AbstractEmailFormPage.settings_panels + [
        MultiFieldPanel(
            [FieldPanel("save_submission")],
            _("Save the submitted data on the webserver (e.g. for CSV export)"),
        )
    ]

    class Meta:
        verbose_name = _("Email Form Page")
        verbose_name_plural = _("Email Form Pages")

    def process_form_submission(self, form):
        submission = self.get_submission_class()(
            form_data=json.dumps(form.cleaned_data, cls=DjangoJSONEncoder), page=self
        )
        if self.save_submission:
            submission.save()
        if self.to_address:
            self.send_mail(form)
        return submission

    def serve(self, request, *args, **kwargs):
        if request.method == "POST":
            form = self.get_form(
                request.POST, request.FILES, page=self, user=request.user
            )

            if form.is_valid():
                self.process_form_submission(form)
                return redirect(
                    self.get_landing_page(request).get_url(), permanent=False
                )
        else:
            form = self.get_form(page=self, user=request.user)

        context = self.get_context(request)
        context["form"] = form
        return render(request, self.get_template(request), context)

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        context.update({"action": self.url, "form_id": "email_form"})
        return context


class NewsletterFormField(NamedAbstractFormField):
    page = ParentalKey(
        "NewsletterFormPage", on_delete=models.CASCADE, related_name="form_fields"
    )

    class Meta:
        unique_together = ("page", "name")
        ordering = ["sort_order"]


class NewsletterFormPage(AbstractEmailFormPage):
    template = "xr_newsletter/pages/newsletter_form.html"
    sendy_list_id = models.CharField(max_length=254, null=True, blank=True)
    mautic_form_id = models.PositiveSmallIntegerField(null=True, blank=True)

    settings_panels = AbstractEmailFormPage.settings_panels + [
        MultiFieldPanel(
            [FieldPanel("sendy_list_id")],
            _("Subscribe to Sendy newsletter list on submit"),
        ),
        MultiFieldPanel(
            [FieldPanel("mautic_form_id")],
            _("Subscribe to Mautic newsletter on submit."),
        ),
    ]

    parent_page_types = [HomePage, HomeSubPage, LocalGroupPage, LocalGroupSubPage]

    base_form_class = WagtailAdminMauticNewsletterFormPageForm

    class Meta:
        verbose_name = _("Newsletter Form Page")
        verbose_name_plural = _("Newsletter Form Pages")

    def serve(self, request, *args, **kwargs):
        if request.method == "POST":
            form = self.get_form(
                request.POST, request.FILES, page=self, user=request.user
            )

            if form.is_valid():
                # form_submission = self.get_submission_class()(
                #     form_data=json.dumps(form.cleaned_data, cls=DjangoJSONEncoder),
                #     page=self,
                # )
                if self.to_address:
                    self.send_mail(form)

                if self.mautic_submit_url:
                    try:
                        data = {
                            "mauticform[f_name]": form.cleaned_data.get("name", None),
                            "mauticform[stadt]": form.cleaned_data.get("city", None),
                            "mauticform[email]": form.cleaned_data.get("email", None),
                            "mauticform[rufnummer1]": form.cleaned_data.get(
                                "phone", None
                            ),
                            "mauticform[formId]": self.mautic_form_id,
                            "mauticform[return]": "",
                            "mauticform[formName]": "inputwebsitenew",
                        }
                        response = requests.post(self.mautic_submit_url, data=data)

                        if response.status_code == 200 and not re.search(
                            "Error", response.text
                        ):
                            return redirect(
                                self.get_landing_page(request).get_url(),
                                permanent=False,
                            )
                    except IndexError:
                        pass

                elif self.sendy_list_id:
                    data = {
                        "email": form.cleaned_data.get("email", None),
                        "name": form.cleaned_data.get("name", None),
                        "gdpr": form.cleaned_data.get("gdpr", None),
                    }
                    try:
                        sendy_response = sendy_api.subscribe(self.sendy_list_id, **data)
                    except ConnectionError:
                        sendy_response = None

                    try:
                        if sendy_response == "true" or int(sendy_response) == 1:
                            return redirect(
                                self.get_landing_page(request).get_url(),
                                permanent=False,
                            )
                    except ValueError:
                        pass

                message = _("Uups, something went wrong. Please try again later.")
                messages.error(request, message)
                # form = self.get_form(page=self, user=request.user)
        else:
            form = self.get_form(page=self, user=request.user)

        context = self.get_context(request)
        context["form"] = form

        return render(request, self.get_template(request), context)

    @property
    def mautic_submit_url(self):
        # e.g. https://mautic.extinctionrebellion.de/form/submit?formId=3
        if not hasattr(settings, "MAUTIC_SUBMIT_URL") or not self.mautic_form_id:
            return None
        return "{}/form/submit?formId={}".format(
            settings.MAUTIC_SUBMIT_URL, self.mautic_form_id
        )

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        context.update({"action": self.url, "form_id": "newsletter_form"})
        if self.mautic_submit_url:
            context.update({"submit_name": "mauticform[submit]"})
        return context


class ThankYouPage(XrPage):
    template = "xr_newsletter/pages/thank_you.html"
    content = StreamField(ContentBlock, blank=True)
    group = models.ForeignKey(LocalGroup, editable=False, on_delete=models.PROTECT)

    content_panels = XrPage.content_panels + [StreamFieldPanel("content")]

    parent_page_types = [EmailFormPage, NewsletterFormPage]

    def save(self, *args, **kwargs):
        if not hasattr(self, "group") or self.group is None:
            self.group = self.get_parent().specific.group

        super().save(*args, **kwargs)

    class Meta:
        verbose_name = _("Thank You Page")
        verbose_name_plural = _("Thank You Pages")
