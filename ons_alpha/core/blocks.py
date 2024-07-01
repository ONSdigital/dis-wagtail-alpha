from django.template.loader import render_to_string
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
        template = "templates/components/streamfield/image_block.html"


class DocumentBlock(blocks.StructBlock):
    document = DocumentChooserBlock()
    title = blocks.CharBlock(required=False)

    class Meta:
        icon = "doc-full-inverse"
        template = "templates/components/streamfield/document_block.html"


class TableBlock(WagtailTableBlock):
    def render(self, value, context=None):
        template = getattr(self.meta, "template", None)
        if template and value:
            table_header = (
                value["data"][0]
                if value.get("data", None)
                and len(value["data"]) > 0
                and value.get("first_row_is_table_header", False)
                else None
            )
            first_col_is_header = value.get("first_col_is_header", False)

            new_context = {} if context is None else dict(context)

            config = {}
            if caption := value.get("table_caption"):
                config["caption"] = caption

            if table_header:
                data = value["data"][1:]
                config["ths"] = [{"value": column} for column in table_header]
            else:
                data = value.get("data", [])

            config["trs"] = [
                {"tds": [{"value": column} for column in row]} for row in data
            ]

            new_context.update(
                {
                    "self": value,
                    self.TEMPLATE_VAR: value,
                    "table_header": table_header,
                    "first_col_is_header": first_col_is_header,
                    "html_renderer": self.is_html_renderer(),
                    "table_caption": value.get("table_caption"),
                    "data": data,
                    "config": config,
                }
            )
            return render_to_string(template, new_context)
        else:
            return self.render_basic(value or "", context=context)

    class Meta:
        template = "templates/components/streamfield/table_block.html"


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

    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context=parent_context)
        table = value["table"]
        config = {}
        if caption := value.get("caption"):
            config["caption"] = caption

        config["ths"] = [{"value": column["heading"]} for column in table.columns]
        config["trs"] = [
            {"tds": [{"value": column} for column in row]} for row in table.rows
        ]
        context["table_config"] = config
        return context

    class Meta:
        icon = "table"
        template = "templates/components/streamfield/typed_table_block.html"


class QuoteBlock(blocks.StructBlock):
    quote = blocks.CharBlock(form_classname="title")
    attribution = blocks.CharBlock(required=False)

    class Meta:
        icon = "openquote"
        template = "templates/components/streamfield/quote_block.html"


class StoryBlock(blocks.StreamBlock):
    """Main StreamField block to be inherited by Pages."""

    heading = blocks.CharBlock(
        form_classname="title",
        icon="title",
        template="templates/components/streamfield/heading_block.html",
    )
    paragraph = blocks.RichTextBlock()
    image = ImageBlock()
    quote = QuoteBlock()
    embed = EmbedBlock()
    call_to_action = SnippetChooserBlock(
        "core.CallToActionSnippet",
        template="templates/components/streamfield/call_to_action_block.html",
    )
    document = DocumentBlock()
    table = TableBlock()
    typed_table = TypedTableBlock(label="Rich text and numeric table block")

    class Meta:
        template = "templates/components/streamfield/stream_block.html"
