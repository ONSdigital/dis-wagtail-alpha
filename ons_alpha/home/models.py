from django.db import models
from wagtail.admin.panels import FieldPanel
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
