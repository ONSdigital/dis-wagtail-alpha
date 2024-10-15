from django.utils.html import format_html, strip_tags
from django.utils.text import slugify
from django.utils.translation import gettext as _
from wagtail.blocks import (
    CharBlock,
    ChoiceBlock,
    DateBlock,
    ListBlock,
    PageChooserBlock,
    StructBlock,
    TextBlock,
)

from ons_alpha.core.constants import CONTENT_TYPE_LABEL_CHOICES


class DocumentListItemBlock(StructBlock):
    title = CharBlock(label=_("Title"), max_length=200, required=True)
    release_date = DateBlock(label=_("Release date"), required=True)
    content_type_label = ChoiceBlock(label=_("Content type label"), choices=CONTENT_TYPE_LABEL_CHOICES, required=True)
    description = TextBlock(label=_("Description"), max_length=300, required=True)
    page = PageChooserBlock(label=_("Page"), required=False)

    class Meta:
        icon = "list-ul"
        label = _("Document")

    def clean(self, value):
        value = super().clean(value)
        value["description"] = strip_tags(value["description"])
        return value


class DocumentListBlock(StructBlock):
    heading = CharBlock(label=_("Heading"), max_length=200)
    documents = ListBlock(DocumentListItemBlock, label=_("Documents"))

    class Meta:
        icon = "list-ul"
        label = _("Document list")
        template = "templates/components/streamfield/document_list_block.html"

    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context=parent_context)
        context["heading"] = value["heading"]
        context["slug"] = slugify(value["heading"])

        # Prepare 'documents' list for the context
        documents = []
        for item in value["documents"]:
            document = {
                "title": {
                    "text": item["title"],
                },
                "description": format_html("<p>{}</p>", item["description"]),
                "metadata": {
                    "object": {
                        "text": item["content_type_label"],
                    },
                    "date": {
                        "prefix": "Released",
                        "showPrefix": True,
                        "iso": item["release_date"].isoformat(),
                        "short": item["release_date"].strftime("%-d %B %Y"),
                    },
                },
            }
            if page := item["page"]:
                document["title"]["url"] = page.specific_deferred.get_url(
                    parent_context.get("request") if parent_context else None
                )
            documents.append(document)

        # Add 'documents' to the context
        context["documents"] = documents

        return context

    def to_table_of_contents_items(self, value):
        return [{"url": "#" + slugify(value["heading"]), "text": value["heading"]}]
