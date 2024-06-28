from wagtail import blocks
from wagtail.contrib.table_block.blocks import TableBlock as WagtailTableBlock
from wagtail.contrib.typed_table_block.blocks import (
    TypedTableBlock as WagtailTypedTableBlock,
)
from wagtail.documents.blocks import DocumentChooserBlock
from wagtail.embeds.blocks import EmbedBlock
from wagtail.images.blocks import ImageChooserBlock
from wagtail.snippets.blocks import SnippetChooserBlock


class ImageBlock(blocks.StructBlock):
    image = ImageChooserBlock()
    caption = blocks.CharBlock(required=False)

    class Meta:
        icon = "image"
        template = "components/streamfield/image_block.html"


class DocumentBlock(blocks.StructBlock):
    document = DocumentChooserBlock()
    title = blocks.CharBlock(required=False)

    class Meta:
        icon = "doc-full-inverse"
        template = "components/streamfield/document_block.html"


class TableBlock(WagtailTableBlock):
    class Meta:
        template = "components/streamfield/table_block.html"


class TypedTableBlock(blocks.StructBlock):
    caption = blocks.CharBlock(required=False)
    table = WagtailTypedTableBlock(
        [
            ("numeric", blocks.FloatBlock()),
            (
                "rich_text",
                blocks.RichTextBlock(
                    features=["bold", "italic", "link", "ol", "ul", "document-link"]
                ),
            ),
        ]
    )

    class Meta:
        icon = "table"
        template = "components/streamfield/typed_table_block.html"


class QuoteBlock(blocks.StructBlock):
    quote = blocks.CharBlock(form_classname="title")
    attribution = blocks.CharBlock(required=False)

    class Meta:
        icon = "openquote"
        template = "components/streamfield/quote_block.html"


class StoryBlock(blocks.StreamBlock):
    """Main StreamField block to be inherited by Pages."""

    heading = blocks.CharBlock(
        form_classname="title",
        icon="title",
        template="components/streamfield/heading_block.html",
    )
    paragraph = blocks.RichTextBlock()
    image = ImageBlock()
    quote = QuoteBlock()
    embed = EmbedBlock()
    call_to_action = SnippetChooserBlock(
        "core.CallToActionSnippet",
        template="components/streamfield/call_to_action_block.html",
    )
    document = DocumentBlock()
    table = TableBlock()
    typed_table = TypedTableBlock(label="Rich text and numeric table block")

    class Meta:
        template = "components/streamfield/stream_block.html"
