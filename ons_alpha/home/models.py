from django.db import models
from django.http import Http404
from wagtail.admin.panels import FieldPanel
from wagtail.models import Locale
from wagtail.search import index

from ons_alpha.core.models import BasePage


class HomePage(BasePage):
    template = "templates/pages/home_page.html"

    # Only allow creating HomePages at the root level
    parent_page_types = ["wagtailcore.Page"]

    strapline = models.CharField(blank=True, max_length=255)
    call_to_action = models.ForeignKey(
        "core.CallToActionSnippet",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    search_fields = BasePage.search_fields + [index.SearchField("strapline")]

    content_panels = BasePage.content_panels + [
        FieldPanel("strapline"),
        FieldPanel("call_to_action"),
    ]

    def route(self, request, path_components):
        try:
            return super().route(request, path_components)
        except Http404 as e:
            # we got a 404, so let's check if this is for a translation
            # and try to serve the default version
            default_locale = Locale.get_default()
            if self.locale_id != default_locale.pk and not default_locale.is_active:
                return self.get_translation(default_locale).route(request, path_components)

            raise e
