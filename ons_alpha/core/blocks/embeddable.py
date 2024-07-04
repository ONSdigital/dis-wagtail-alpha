from django.core.exceptions import ValidationError
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


class DocumentBlock(blocks.StructBlock):
    document = DocumentChooserBlock()
    title = blocks.CharBlock(required=False)

    class Meta:
        icon = "doc-full-inverse"
        template = "templates/components/streamfield/document_block.html"


ONS_EMBED_PREFIX = "https://www.ons.gov.uk/visualisations/"


class ONSEmbedBlock(blocks.StructBlock):
    url = blocks.URLBlock(help_text=f"Must start with <code>{ ONS_EMBED_PREFIX }</code> to your URL.")
    title = blocks.CharBlock(default="Interactive chart")

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
