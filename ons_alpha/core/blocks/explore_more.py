from django.core.exceptions import ValidationError
from django.utils.html import format_html, strip_tags
from django.utils.text import slugify
from django.utils.translation import gettext as _
from wagtail.blocks import CharBlock, ListBlock, PageChooserBlock, StructBlock, TextBlock, URLBlock
from wagtail.images.blocks import ImageChooserBlock


class ExploreMoreListItemBlock(StructBlock):
    title = CharBlock(label=_("Title"), max_length=200, required=True)
    thumbnail = ImageChooserBlock(label=_("Thumbnail"), required=True)
    description = TextBlock(label=_("Description"), max_length=300, required=True)
    page = PageChooserBlock(
        label=_("Page"),
        required=False,
        help_text=_("Select a page to link to. This will be used as the URL."),
    )
    external_link = URLBlock(
        label=_("External link"),
        required=False,
        help_text=_("Enter an external URL to link to."),
    )

    class Meta:
        icon = "list-ul"
        label = _("Explore more item")

    def clean(self, value):
        value = super().clean(value)
        value["description"] = strip_tags(value["description"])
        # Ensure only one of page or external_link is provided
        if value["page"] and value["external_link"]:
            raise ValidationError(_("You cannot provide both a page and an external link at the same time."))
        return value


class ExploreMoreBlock(StructBlock):
    """Variant of DocumentListBlock that includes thumbnails, and no metadata.

    Both use the same DS Document List Block template and macro.
    """

    heading = CharBlock(label=_("Heading"), max_length=200, required=True)
    documents = ListBlock(ExploreMoreListItemBlock, label=_("Documents"))

    class Meta:
        icon = "list-ul"
        label = _("Explore more")
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
                    "url": item["page"].url if item["page"] else item["external_link"],
                },
                "description": format_html("<p>{}</p>", item["description"]),
                "metadata": {},
                "thumbnail": {
                    # standard: 136×96
                    # high-dpi: 272×192
                    "smallSrc": item["thumbnail"].get_rendition("fill-136x96").url,
                    "largeSrc": item["thumbnail"].get_rendition("fill-272x192").url,
                },
            }
            documents.append(document)

        # Add 'documents' to the context
        context["documents"] = documents

        return context

    def to_table_of_contents_items(self, value):
        return [{"url": "#" + slugify(value["heading"]), "text": value["heading"]}]
