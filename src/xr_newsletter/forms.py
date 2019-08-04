from django.core.exceptions import NON_FIELD_ERRORS
from django.forms import ValidationError
from django.utils.translation import ugettext as _
from wagtail.contrib.forms.forms import WagtailAdminFormPageForm, FormBuilder


class WagtailAdminGdprFormPageForm(WagtailAdminFormPageForm):
    required_fields = ["gdpr"]
    required_fields_required = ["gdpr"]

    def __init__(self, data=None, files=None, parent_page=None, *args, **kwargs):
        instance = kwargs["instance"]

        if not instance.form_fields.exists():
            form_fields = self.get_form_fields()
            instance.form_fields.set(form_fields)

        super().__init__(data, files, parent_page, *args, **kwargs)

    @staticmethod
    def get_form_fields():
        from xr_newsletter.models import NewsletterFormField

        form_fields = [
            NewsletterFormField(
                label=_("I agree"),
                name="gdpr",
                field_type="checkbox",
                required=True,
                help_text=_(
                    "GDPR Permission: I give my consent to Extinction Rebellion to "
                    "get in touch with me using the information I have provided in "
                    "this form, for the purpose of news, updates, and rebellion."
                ),
                sort_order=0,
            )
        ]
        return form_fields

    def clean(self):
        super().clean()

        # Check for dupe form field labels - fixes #585
        if "form_fields" in self.formsets:
            _forms = self.formsets["form_fields"].forms
            for f in _forms:
                f.is_valid()

            # Check for duplicate field names
            for i, form in enumerate(_forms):
                if "name" in form.changed_data:
                    name = form.cleaned_data.get("name")
                    for idx, ff in enumerate(_forms):
                        # Exclude self
                        if idx != i and name == ff.cleaned_data.get("name"):
                            form.add_error(
                                "name",
                                ValidationError(
                                    _(
                                        "There is another field with the name %s, "
                                        "please change one of them." % name
                                    )
                                ),
                            )

            # check for required form fields

            found_field_forms = {}

            for form in _forms:
                name = form.cleaned_data.get("name")
                if name in self.required_fields:
                    found_field_forms[name] = form

            for field_name in self.required_fields:
                if field_name not in found_field_forms:
                    self.add_error(
                        NON_FIELD_ERRORS,
                        ValidationError(
                            'A form field with the name "%s" is required.' % field_name
                        ),
                    )

            for field_name in self.required_fields_required:
                form = found_field_forms.get(field_name, None)

                if form and not form.cleaned_data.get("required"):
                    form.add_error(
                        "required",
                        ValidationError(
                            'The "%s" form field must be set required.' % field_name
                        ),
                    )
                    self.add_error(
                        NON_FIELD_ERRORS,
                        ValidationError(
                            'The "%s" form field must be set required.' % field_name
                        ),
                    )

            gdpr_field = found_field_forms.get("gdpr", None)

            if (
                gdpr_field
                and not gdpr_field.cleaned_data.get("field_type") == "checkbox"
            ):
                gdpr_field.add_error(
                    "field_type",
                    ValidationError(
                        'The "gdpr" form field must be of type "checkbox".'
                    ),
                )
                self.add_error(
                    NON_FIELD_ERRORS,
                    ValidationError(
                        'The "gdpr" form field must be of type "checkbox".'
                    ),
                )


class WagtailAdminSendyNewsletterFormPageForm(WagtailAdminGdprFormPageForm):
    required_fields = ["email", "name", "gdpr"]
    required_fields_required = ["email", "gdpr"]

    @staticmethod
    def get_form_fields():
        from xr_newsletter.models import NewsletterFormField

        form_fields = [
            NewsletterFormField(
                label=_("Email"),
                name="email",
                field_type="email",
                required=True,
                sort_order=0,
            ),
            NewsletterFormField(
                label=_("Name"),
                name="name",
                field_type="singleline",
                required=False,
                sort_order=1,
            ),
            NewsletterFormField(
                label=_("I agree"),
                name="gdpr",
                field_type="checkbox",
                required=True,
                help_text=_(
                    "GDPR Permission: I give my consent to Extinction Rebellion to "
                    "get in touch with me using the information I have provided in "
                    "this form, for the purpose of news, updates, and rebellion."
                ),
                sort_order=2,
            ),
        ]
        return form_fields


class WagtailAdminMauticNewsletterFormPageForm(WagtailAdminGdprFormPageForm):
    required_fields = ["email", "name", "gdpr", "city", "phone"]
    required_fields_required = ["email", "gdpr"]

    @staticmethod
    def get_form_fields():
        from xr_newsletter.models import NewsletterFormField

        form_fields = [
            NewsletterFormField(
                label=_("Name"),
                name="name",
                field_type="singleline",
                required=False,
                sort_order=1,
            ),
            NewsletterFormField(
                label=_("City"),
                name="city",
                field_type="singleline",
                required=False,
                sort_order=2,
            ),
            NewsletterFormField(
                label=_("Email"),
                name="email",
                field_type="email",
                required=True,
                sort_order=0,
            ),
            NewsletterFormField(
                label=_("Phone"),
                name="phone",
                field_type="singleline",
                required=False,
                sort_order=3,
            ),
            NewsletterFormField(
                label=_("Data policy"),
                name="gdpr",
                field_type="checkbox",
                required=True,
                help_text=_(
                    "GDPR Permission: I give my consent to Extinction Rebellion to "
                    "get in touch with me using the information I have provided in "
                    "this form, for the purpose of news, updates, and rebellion."
                ),
                sort_order=4,
            ),
        ]
        return form_fields


class PlaceholderFormBuilder(FormBuilder):
    @property
    def formfields(self):
        formfields = super().formfields

        for field in self.fields:
            if field.placeholder:
                formfields[field.clean_name].widget.attrs.update(
                    {"placeholder": field.placeholder}
                )
            if field.size:
                formfields[field.clean_name].size = field.size

        return formfields
