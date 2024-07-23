from ons_alpha.core.models.base import BasePage
from ons_alpha.core.models.mixins import SubpageMixin

from wagtail.admin.panels import FieldPanel
from django.db import models


def get_context(self, request, *args, **kwargs):
    context = super().get_context(request, *args, **kwargs)

    context["toc"] = self.toc

    return context

class TopicPage(SubpageMixin, BasePage):
    template = "templates/pages/topics/topic_page.html"
    parent_page_types = ["topics.TopicSectionPage"]
    subpage_types = ["topics.TopicPage"]
    summary = models.CharField(blank=True, max_length=100)

    page_description = "A specific topic page. e.g.  Public sector finance or  Inflation and price indices"

    content_panels = BasePage.content_panels + [
            FieldPanel("summary"),
        ]


class TopicSectionPage(SubpageMixin, BasePage):
    template = "templates/pages/topics/topic_section_page.html"
    subpage_types = ["topics.TopicSectionPage", "topics.TopicPage"]


    page_description = "General topic page. e.g. Economy"
    summary = models.CharField(blank=True, max_length=100)

    content_panels = BasePage.content_panels + [
        FieldPanel("summary"),
    ]



