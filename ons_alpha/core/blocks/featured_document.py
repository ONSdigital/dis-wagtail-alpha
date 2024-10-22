from django.utils.text import slugify
from django.utils.translation import gettext as _
from wagtail.blocks import ChoiceBlock, PageChooserBlock, RichTextBlock, StructBlock

from ons_alpha.core.constants import CONTENT_TYPE_LABEL_CHOICES


class FeaturedDocumentBlock(StructBlock):
    page = PageChooserBlock(label=_("Page"), required=True)
    content_type_label = ChoiceBlock(label=_("Content type label"), choices=CONTENT_TYPE_LABEL_CHOICES, required=True)
    description = RichTextBlock(label=_("Description"), required=True, features=["ol", "ul"])

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
