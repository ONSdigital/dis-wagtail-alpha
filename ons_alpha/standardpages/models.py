from django.conf import settings
from django.core.paginator import Paginator
from django.db import models
from wagtail.admin.panels import FieldPanel, InlinePanel
from wagtail.search import index

from ons_alpha.core.models import BasePage
from ons_alpha.utils.fields import StreamField

from .blocks import StoryBlock


class InformationPage(BasePage):
    template = "templates/pages/information_page.html"

    introduction = models.TextField(blank=True)
    body = StreamField(StoryBlock(), use_json_field=True)

    search_fields = BasePage.search_fields + [
        index.SearchField("introduction"),
        index.SearchField("body"),
    ]

    content_panels = BasePage.content_panels + [
        FieldPanel("introduction"),
        FieldPanel("body"),
        InlinePanel("page_related_pages", label="Related pages"),
    ]

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        context["related_pages"] = [
            {
                "text": page.listing_title or page.title,
                "url": page.get_full_url(request),
            }
            for page in self.related_pages
        ]

        return context


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
