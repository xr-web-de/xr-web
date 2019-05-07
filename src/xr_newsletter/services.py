from django.conf import settings
from sendy.api import SendyAPI
from sendy.binder import bind_api


class XRSendyAPI(SendyAPI):
    subscribe = bind_api(
        path="subscribe",
        allowed_param=["list", "email", "name", "gdpr", "referrer"],
        extra_param={"boolean": "true"},
        success_message="true",
        require_auth=False,
        method="POST",
    )


try:
    if settings.DEBUG or settings.TESTING:
        sendy_api = XRSendyAPI(
            host=settings.SENDY_HOST_URL, api_key=settings.SENDY_API_KEY, debug=True
        )
    else:
        sendy_api = XRSendyAPI(
            host=settings.SENDY_HOST_URL, api_key=settings.SENDY_API_KEY
        )
except (ImportError, AttributeError) as e:
    print("Warnung: sendy scheint nicht installiert zu sein." + str(e))
