from django.test import RequestFactory, TestCase
from wagtail.models import Site

from ons_alpha.core.context_processors import global_vars
from ons_alpha.core.models import Tracking


class GlobalVarsContextProcessorTest(TestCase):
    def test_when_no_tracking_settings_defined(self):
        request = RequestFactory().get("/")
        self.assertEqual(
            global_vars(request),
            {"GOOGLE_TAG_MANAGER_ID": "", "SEO_NOINDEX": True, "LANGUAGE_CODE": "en-gb", "IS_EXTERNAL_ENV": False},
        )

    def test_when_tracking_settings_defined(self):
        Tracking.objects.create(
            site=Site.objects.get(is_default_site=True),
            google_tag_manager_id="GTM-123456",
        )
        request = RequestFactory().get("/")
        self.assertEqual(
            global_vars(request),
            {
                "GOOGLE_TAG_MANAGER_ID": "GTM-123456",
                "SEO_NOINDEX": True,
                "LANGUAGE_CODE": "en-gb",
                "IS_EXTERNAL_ENV": False,
            },
        )
