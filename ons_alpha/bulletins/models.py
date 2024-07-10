from functools import cached_property

from django.db import models
from wagtail.admin.panels import FieldPanel, FieldRowPanel, MultiFieldPanel, ObjectList, TabbedInterface

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
                FieldRowPanel(
                    [
                        FieldPanel("release_date"),
                        FieldPanel("next_release_date"),
                    ]
                ),
                FieldPanel("is_accredited"),
                FieldPanel("contact_details"),
            ],
            heading="Metadata",
        ),
        FieldPanel("body"),
    ]

    edit_handler = TabbedInterface(
        [
            ObjectList(content_panels, heading="Content"),
            ObjectList(
                [FieldPanel("updates", help_text="Add any corrections or updates")], heading="Corrections & Updates"
            ),
            ObjectList(BasePage.promote_panels, heading="Promote"),
            ObjectList(BasePage.settings_panels, heading="Settings", classname="settings"),
        ]
    )

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)

        context["toc"] = self.toc

        return context

    @cached_property
    def toc(self):
        items = [{"url": "#summary", "text": "Summary"}]

        for block in self.body:  # pylint: disable=not-an-iterable
            if hasattr(block.block, "to_table_of_contents_items"):
                items += block.block.to_table_of_contents_items(block.value)

        if self.contact_details_id:
            items += [{"url": "#contact-details", "text": "Contact details"}]

        return items
