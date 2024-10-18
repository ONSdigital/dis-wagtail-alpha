from django.db import models
from django.http import Http404
from wagtail.admin.panels import FieldPanel
from wagtail.models import Locale
from wagtail.search import index

from ons_alpha.core.blocks.stream_blocks import SimpleStoryBlock
from ons_alpha.core.models import BasePage
from ons_alpha.utils.fields import StreamField


class HomePage(BasePage):
    template = "templates/pages/home_page.html"

    # Only allow creating HomePages at the root level
    parent_page_types = ["wagtailcore.Page"]

    strapline = models.CharField(
        blank=True,
        max_length=255,
        help_text="An alternative title to be used as the h1. If not specified, the page title will be used.",
    )
    summary = models.TextField(blank=True)
    body = StreamField(SimpleStoryBlock, null=True)

    search_fields = BasePage.search_fields + [
        index.SearchField("strapline"),
        index.SearchField("summary"),
        index.SearchField("body"),
    ]

    content_panels = BasePage.content_panels + [
        FieldPanel("strapline"),
        FieldPanel("summary"),
        FieldPanel("body"),
    ]

    @property
    def h1(self) -> str:
        return self.strapline or self.title

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
