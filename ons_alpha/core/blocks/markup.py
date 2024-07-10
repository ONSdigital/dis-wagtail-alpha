from django.utils.text import slugify
from wagtail import blocks
from wagtail.contrib.table_block.blocks import DEFAULT_TABLE_OPTIONS
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

    def __init__(self, required=True, help_text=None, table_options=None, **kwargs):
        if table_options is None:
            table_options = {
                "mergeCells": True,
                "contextMenu": DEFAULT_TABLE_OPTIONS["contextMenu"] + ["---------", "mergeCells", "alignment"],
            }

        super().__init__(required=required, help_text=help_text, table_options=table_options, **kwargs)

    def _to_ons_classname(self, classname: str) -> str:
        """
        Reference: https://handsontable.com/docs/javascript-data-grid/text-alignment/#horizontal-and-vertical-alignment
        """
        match classname:
            case "htRight":
                return "ons-u-ta-right"
            case "htLeft":
                return "ons-u-ta-left"
            case "htCenter":
                return "ons-u-ta-center"
            case _:
                return ""

    def _get_rows(self, value, table_header, classnames):
        trs = []
        data = value["data"][1:] if table_header else value.get("data", [])
        for row_idx, row in enumerate(data, 1 if table_header else 0):
            tds = []
            for cell_idx, cell in enumerate(row):
                td = {"value": cell}
                if classname := classnames.get((row_idx, cell_idx)):
                    td["tdClasses"] = classname
                tds.append(td)

            trs.append({"tds": tds})
        return trs

    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context=parent_context)

        classnames = {}
        hidden = {}
        spans = {}
        if value.get("cell"):
            for meta in value["cell"]:
                if "className" in meta:
                    classnames[(meta["row"], meta["col"])] = self._to_ons_classname(meta["className"])
                if "hidden" in meta:
                    hidden[(meta["row"], meta["col"])] = meta["hidden"]

        if value.get("mergeCells"):
            for merge in value["mergeCells"]:
                spans[(merge["row"], merge["col"])] = {
                    "rowspan": merge["rowspan"],
                    "colspan": merge["colspan"],
                }

        table_header = (
            [{"value": cell or ""} for cell in value["data"][0]]
            if value.get("data", "") and len(value["data"]) > 0 and value.get("first_row_is_table_header", False)
            else []
        )

        # Note: update when https://service-manual.ons.gov.uk/design-system/components/table supports col/row spans
        return {
            "options": {
                "caption": value.get("table_caption"),
                "ths": table_header,
                "trs": self._get_rows(value, table_header, classnames),
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
