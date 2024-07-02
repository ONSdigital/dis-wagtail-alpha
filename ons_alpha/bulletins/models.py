from django.db import models
from wagtail.admin.panels import FieldPanel, MultiFieldPanel

from ons_alpha.core.models.base import BasePage
from ons_alpha.utils.fields import StreamField

from .blocks import BulletinStoryBlock


class BulletinPage(BasePage):
    template = "templates/pages/bulletins/bulletin_page.html"
    parent_page_types = ["topics.TopicPage"]

    summary = models.TextField()

    release_date = models.DateField()
    next_release_date = models.DateField()

    body = StreamField(BulletinStoryBlock(), use_json_field=True)

    content_panels = BasePage.content_panels + [
        FieldPanel("summary"),
        MultiFieldPanel(
            [
                FieldPanel("release_date"),
                FieldPanel("next_release_date"),
            ],
            heading="Release dates",
        ),
        FieldPanel("body"),
    ]
