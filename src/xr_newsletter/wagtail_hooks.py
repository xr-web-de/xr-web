from django.conf import settings
from django.utils.translation import ugettext as _
from urllib3.exceptions import NewConnectionError, MaxRetryError
from wagtail.admin import messages
from wagtail.core import hooks

from xr_newsletter.models import NewsletterFormPage
from xr_newsletter.services import sendy_api


@hooks.register("after_create_page")
@hooks.register("after_edit_page")
def newsletter_form_page_check_sendy_api(request, page):

    if isinstance(page, NewsletterFormPage):
        if not page.sendy_list_id:
            message = _(
                'There is no sendy_list_id set for page "%s". '
                "Therefore newsletter subscription will not work." % page
            )
            messages.warning(request, message)
        elif not settings.DEBUG:

            sendy_response = None
            try:
                sendy_response = sendy_api.subscriber_count(page.sendy_list_id)

                # Sendy will return an integer if the given list_id exists

                int(sendy_response)
            except (
                ConnectionError,
                NewConnectionError,
                MaxRetryError,
                ValueError,
            ) as e:
                message = (
                    _(
                        "There was a problem talking to Sendy API: %s. "
                        "Please check the sendy_list_id and try again."
                    )
                    % sendy_response
                    if sendy_response
                    else e
                )
                messages.warning(request, message)
