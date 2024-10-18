from django.conf import settings
from django.core.paginator import Paginator
from django.db import models
from wagtail.admin.panels import FieldPanel
from wagtail.search import index

from ons_alpha.core.blocks.stream_blocks import SimpleStoryBlock
from ons_alpha.core.models import BasePage
from ons_alpha.utils.fields import StreamField


class InformationPage(BasePage):
    template = "templates/pages/information_page.html"

    strapline = models.CharField(
        blank=True,
        max_length=255,
        help_text="An alternative title to be used as the h1. If not specified, the page title will be used.",
    )
    summary = models.TextField(blank=True)
    body = StreamField(SimpleStoryBlock)

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


class IndexPage(BasePage):
    template = "templates/pages/index_page.html"

    introduction = models.TextField(blank=True)

    content_panels = BasePage.content_panels + [FieldPanel("introduction")]

    search_fields = BasePage.search_fields + [index.SearchField("introduction")]

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        subpages = self.get_children().live()
        per_page = settings.DEFAULT_PER_PAGE
        page_number = request.GET.get("page")
        subpages = Paginator(subpages, per_page).get_page(page_number)

        context["subpages"] = subpages

        return context
