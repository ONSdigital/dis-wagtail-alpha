from django.conf import settings
from django.core.exceptions import ValidationError
from django.template.defaultfilters import filesizeformat
from wagtail import blocks
from wagtail.blocks import StructBlockValidationError
from wagtail.documents.blocks import DocumentChooserBlock
from wagtail.images.blocks import ImageChooserBlock


class ImageBlock(blocks.StructBlock):
    image = ImageChooserBlock()
    caption = blocks.CharBlock(required=False)

    class Meta:
        icon = "image"
        template = "templates/components/streamfield/image_block.html"


class DocumentBlockStructValue(blocks.StructValue):
    def as_macro_data(self):
        return {
            "thumbnail": True,
            "title": {
                "text": self["title"] or self["document"].title,
                "url": self["document"].url,
            },
            "description": self["description"],
            "metadata": {
                "file": {
                    "fileType": self["document"].file_extension.upper(),
                    "fileSize": filesizeformat(self["document"].get_file_size()),
                }
            },
        }


class DocumentBlock(blocks.StructBlock):
    document = DocumentChooserBlock()
    title = blocks.CharBlock(required=False)
    description = blocks.RichTextBlock(features=settings.RICH_TEXT_BASIC, required=False)

    class Meta:
        icon = "doc-full-inverse"
        value_class = DocumentBlockStructValue
        template = "templates/components/streamfield/document_block.html"


class DocumentsBlock(blocks.StreamBlock):
    document = DocumentBlock()

    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context)
        context["macro_data"] = [document.value.as_macro_data() for document in value]
        return context

    class Meta:
        block_counts = {"document": {"min_num": 1}}
        icon = "doc-full-inverse"
        template = "templates/components/streamfield/documents_block.html"


ONS_EMBED_PREFIX = "https://www.ons.gov.uk/"


class ONSEmbedBlock(blocks.StructBlock):
    url = blocks.URLBlock(label="URL", help_text=f"Must start with <code>{ ONS_EMBED_PREFIX }</code> to your URL.")
    title = blocks.CharBlock(default="Embedded content")

    def clean(self, value):
        errors = {}

        if not value["url"].startswith(ONS_EMBED_PREFIX):
            errors["url"] = ValidationError(f"The URL must start with {ONS_EMBED_PREFIX}")

        if errors:
            raise StructBlockValidationError(errors)

        return super().clean(value)

    class Meta:
        icon = "code"
        template = "templates/components/streamfield/ons_embed_block.html"


class ONSChartEmbedBlock(ONSEmbedBlock):
    title = blocks.CharBlock(
        default="Interactive chart",
        help_text="Title for the embedded chart e.g. 'Online sales rose for most main sectors'",
    )
    chart_title = blocks.CharBlock(
        help_text="""
            Detailed chart title, e.g.
            'Figure 3: Value sales, monthly percentage change, seasonally adjusted, Great Britain, July 2024'
            """
    )
    downloads_heading = blocks.CharBlock(default="Download Figure X data")
    downloads_content = blocks.RichTextBlock(features=settings.RICH_TEXT_BASIC)
    footnotes = blocks.RichTextBlock(features=settings.RICH_TEXT_BASIC, required=False)

    class Meta:
        icon = "code"
        template = "templates/components/streamfield/ons_chart_embed_block.html"
