from django.utils.text import slugify
from wagtail import blocks
from wagtail.contrib.table_block.blocks import TableBlock as WagtailTableBlock
from wagtail.contrib.typed_table_block.blocks import (
    TypedTableBlock as WagtailTypedTableBlock,
)


class HeadingBlock(blocks.CharBlock):
    class Meta:
        icon = "title"
        form_classname = "title"
        template = "templates/components/streamfield/heading_block.html"

    def __init__(self, **kwargs):
        self.show_back_to_toc = kwargs.pop("show_back_to_toc", False)

        super().__init__(**kwargs)

    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context=parent_context)
        context["show_back_to_toc"] = self.show_back_to_toc

        return context

    def to_table_of_contents_items(self, value):
        return [{"url": "#" + slugify(value), "text": value}]


class TableBlock(WagtailTableBlock):
    class Meta:
        icon = "info-circle"
        template = "templates/components/streamfield/table_block.html"

    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context)  #

        table_header = (
            [{"value": cell} for cell in value["data"][0]]
            if value.get("data", None) and len(value["data"]) > 0 and value.get("first_row_is_table_header", False)
            else []
        )

        return {
            "options": {
                "caption": value.get("table_caption"),
                "ths": table_header,
                "trs": [
                    {"tds": [{"value": cell} for cell in row]}
                    for row in (value["data"][1:] if table_header else value.get("data", []))
                ],
            },
            **context,
        }

    def render(self, value, context=None):
        # TableBlock has a very custom `render` method. We don't want that
        return super(blocks.FieldBlock, self).render(value, context)


class TypedTableBlock(blocks.StructBlock):
    caption = blocks.CharBlock(required=False)
    table = WagtailTypedTableBlock(
        [
            ("numeric", blocks.FloatBlock()),
            (
                "rich_text",
                blocks.RichTextBlock(features=["bold", "italic", "link", "ol", "ul", "document-link"]),
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
        config["trs"] = [{"tds": [{"value": column} for column in row]} for row in table.rows]
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
