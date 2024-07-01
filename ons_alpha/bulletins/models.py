from django.db import models
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.blocks import RichTextBlock

from ons_alpha.core.blocks import (
    HeadingBlock,
    PanelBlock,
    TableBlock,
)
from ons_alpha.core.models.base import BasePage
from ons_alpha.utils.fields import StreamField


class BulletinPage(BasePage):
    template = "templates/pages/bulletins/bulletin_page.html"
    parent_page_types = ["topics.TopicPage"]

    release_date = models.DateField()
    next_release_date = models.DateField()

    body = StreamField(
        [
            ("heading", HeadingBlock()),
            ("rich_text", RichTextBlock()),
            ("panel", PanelBlock()),
            ("table", TableBlock()),
        ],
        use_json_field=True,
    )

    content_panels = BasePage.content_panels + [
        MultiFieldPanel(
            [
                FieldPanel("release_date"),
                FieldPanel("next_release_date"),
            ],
            heading="Release dates",
        ),
        FieldPanel("body"),
    ]
