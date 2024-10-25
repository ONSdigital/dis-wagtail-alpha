from django.conf import settings
from django.urls import reverse

from ons_alpha.core.models import Tracking


def global_vars(request):
    tracking = Tracking.for_request(request)
    return {
        "GOOGLE_TAG_MANAGER_ID": getattr(tracking, "google_tag_manager_id", None),
        "SEO_NOINDEX": settings.SEO_NOINDEX,
        "LANGUAGE_CODE": settings.LANGUAGE_CODE,
        "IS_EXTERNAL_ENV": settings.IS_EXTERNAL_ENV,
        "TOPIC_PAGE_URL": settings.ONS_TOPIC_PAGE_URL,
        "COOKIE_BANNER_ENABLED": settings.ONS_COOKIE_BANNER_ENABLED,
        "COOKIE_BANNER_SERVICE_NAME": settings.ONS_COOKIE_BANNER_SERVICE_NAME or request.get_host(),
        "MANAGE_COOKIE_SETTINGS_URL": reverse("manage-cookie-settings"),
    }
