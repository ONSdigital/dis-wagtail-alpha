from functools import cached_property

from django.db import models
from wagtail.admin.panels import (
    FieldPanel,
    MultiFieldPanel,
    MultipleChooserPanel,
    ObjectList,
    TabbedInterface,
)
from wagtail.search import index

from ons_alpha.bundles.models import BundledPageMixin
from ons_alpha.charts.utils import streamvalue_includes_highcharts_chart
from ons_alpha.core.blocks.stream_blocks import CoreStoryBlock
from ons_alpha.core.models.base import BasePage
from ons_alpha.taxonomy.forms import PageWithTopicsAdminForm
from ons_alpha.utils.fields import StreamField


class MethodologyPage(BundledPageMixin, BasePage):
    base_form_class = PageWithTopicsAdminForm
    template = "templates/pages/methodology_page.html"
    parent_page_types = ["topics.TopicPage"]
    subpage_types = []

    summary = models.TextField()
    last_revised_date = models.DateField(blank=True, null=True)
    how_it_was_compiled = models.CharField(blank=True, max_length=255)
    geographic_coverage = models.CharField(blank=True, max_length=255)

    contact_details = models.ForeignKey(
        "core.ContactDetails",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    is_accredited = models.BooleanField(default=False)

    body = StreamField(CoreStoryBlock(), use_json_field=True)

    content_panels = (
        BasePage.content_panels
        + BundledPageMixin.panels
        + [
            FieldPanel("summary"),
            MultiFieldPanel(
                [
                    FieldPanel("last_revised_date"),
                    FieldPanel(
                        "is_accredited", help_text="If ticked, will show the official statistics accredited logo."
                    ),
                    FieldPanel("how_it_was_compiled"),
                    FieldPanel("geographic_coverage"),
                    FieldPanel("contact_details"),
                ],
                heading="Metadata",
            ),
            FieldPanel("body"),
        ]
    )

    edit_handler = TabbedInterface(
        [
            ObjectList(content_panels, heading="Content"),
            ObjectList(
                [
                    MultipleChooserPanel("topics", label="Topic", chooser_field_name="topic"),
                ],
                help_text="Select the topics that this bulletin relates to.",
                heading="Taxonomy",
            ),
            ObjectList(BasePage.promote_panels, heading="Promote"),
            ObjectList(BasePage.settings_panels, heading="Settings", classname="settings"),
        ]
    )

    search_fields = BasePage.search_fields + [
        index.SearchField("summary"),
        index.SearchField("body"),
    ]

    @property
    def has_background_info(self):
        return self.is_accredited or self.how_it_was_compiled or self.geographic_coverage

    @cached_property
    def toc(self):
        items = [{"url": "#summary", "text": "Summary"}]

        if self.has_background_info:
            items += [{"url": "#background", "text": "Methodology background"}]

        for block in self.body:  # pylint: disable=not-an-iterable,useless-suppression
            if hasattr(block.block, "to_table_of_contents_items"):
                items += block.block.to_table_of_contents_items(block.value)
        if self.contact_details_id:
            items += [{"url": "#contact-details", "text": "Contact details"}]
        return items

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        context["toc"] = self.toc
        context["has_background_info"] = self.has_background_info
        context["load_highcharts_js"] = streamvalue_includes_highcharts_chart(self.body)
        return context
