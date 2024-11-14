from django.utils.text import slugify
from django.utils.translation import gettext as _
from wagtail import blocks

from ons_alpha.core.constants import CONTENT_TYPE_LABEL_CHOICES


class FeaturedDocumentBlock(blocks.StructBlock):
    page = blocks.PageChooserBlock(label=_("Page"), required=True)
    content_type_label = blocks.ChoiceBlock(
        label=_("Content type label"), choices=CONTENT_TYPE_LABEL_CHOICES, required=True
    )
    description = blocks.RichTextBlock(label=_("Description"), required=True, features=["ol", "ul"])

    class Meta:
        icon = "list-ul"
        label = _("Featured document")
        template = "templates/components/streamfield/featured_document_block.html"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.heading = _("Featured")
        self.slug = slugify(self.heading)

    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context=parent_context)
        context["heading"] = self.heading
        context["slug"] = self.slug

        # Prepare 'document' object for the context
        page = value["page"].specific
        document = {
            "title": {
                "text": page.title,
                "url": page.get_url(parent_context.get("request") if parent_context else None),
            },
            "featured": True,
            "description": value["description"],
            "metadata": {
                "object": {"text": value["content_type_label"]},
            },
        }
        if release_date := getattr(page, "release_date", None):
            document["metadata"]["date"] = {
                "prefix": "Released",
                "showPrefix": True,
                "iso": release_date.isoformat(),
                "short": release_date.strftime("%-d %B %Y"),
            }

        # Add 'documents' to the context
        context["documents"] = [document]

        return context

    def to_table_of_contents_items(self, value):  # pylint: disable=unused-argument
        return [{"url": "#" + self.slug, "text": self.heading}]


class FeaturedDocumentWithChartBlock(FeaturedDocumentBlock):
    chart_url = blocks.URLBlock(label=_("Chart URL"), required=True)
    chart_release_date = blocks.DateBlock(label=_("Release date"), required=True)
    chart_initial_height = blocks.IntegerBlock(
        label="Initial chart height (px)",
        help_text=("NOTE: The chart embed will remain at this height when JS is disabled."),
        required=True,
        default=360,
        min_value=100,
        max_value=1000,
    )

    class Meta:
        icon = "code"
        label = _("Featured document (with chart)")
        template = "templates/components/streamfield/featured_chart_block.html"

    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context=parent_context)
        page = value["page"].specific
        context["link_title"] = page.title
        context["link_url"] = page.get_url(parent_context.get("request") if parent_context else None)
        return context
