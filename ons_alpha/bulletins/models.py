from django.db import models
from wagtail.admin.panels import FieldPanel, MultiFieldPanel

from ons_alpha.core.models.base import BasePage
from ons_alpha.utils.fields import StreamField

from .blocks import BulletinStoryBlock, CorrectionsNoticesStoryBlock


class BulletinPage(BasePage):
    template = "templates/pages/bulletins/bulletin_page.html"
    parent_page_types = ["topics.TopicPage"]

    summary = models.TextField()

    release_date = models.DateField()
    next_release_date = models.DateField()

    contact_details = models.ForeignKey(
        "core.ContactDetails",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    is_accredited = models.BooleanField(default=False)

    body = StreamField(BulletinStoryBlock(), use_json_field=True)

    updates = StreamField(CorrectionsNoticesStoryBlock(), blank=True, use_json_field=True)

    content_panels = BasePage.content_panels + [
        FieldPanel("summary"),
        MultiFieldPanel(
            [
                FieldPanel("release_date"),
                FieldPanel("next_release_date"),
            ],
            heading="Release dates",
        ),
        FieldPanel("is_accredited"),
        FieldPanel("contact_details"),
        FieldPanel("body"),
    ]
