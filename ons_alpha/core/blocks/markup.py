from django.core.exceptions import ValidationError
from django.utils.safestring import mark_safe
from django.utils.text import slugify
from wagtail import blocks
from wagtail.contrib.table_block.blocks import DEFAULT_TABLE_OPTIONS
from wagtail.contrib.table_block.blocks import TableBlock as WagtailTableBlock
from wagtail.contrib.typed_table_block.blocks import TypedTableBlock as WagtailTypedTableBlock


class HeadingBlock(blocks.CharBlock):
    class Meta:
        icon = "title"
        form_classname = "title"
        template = "templates/components/streamfield/heading_block.html"
        label = "Section heading"

    def __init__(self, **kwargs):
        self.show_back_to_toc = kwargs.pop("show_back_to_toc", False)
        kwargs["help_text"] = kwargs.pop("help_text", "This is output as level 2 heading (<code>h2</code>)")

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

    def _get_header(
        self, value, hidden: dict[tuple[int, int], bool], spans: dict[tuple[int, int], str]
    ) -> list[dict[str, str]]:
        table_header = []
        if value.get("data", "") and len(value["data"]) > 0 and value.get("first_row_is_table_header", False):
            for th_idx, cell in enumerate(value["data"][0]):
                key = (0, th_idx)
                if hidden.get(key):
                    continue

                th = {"value": cell or ""}
                if span := spans.get(key):
                    th["span"] = span
                table_header.append(th)
        return table_header

    def _get_rows(self, value, classnames, hidden, spans):  # pylint: disable=too-many-locals
        trs = []
        has_header = value.get("data", "") and len(value["data"]) > 0 and value.get("first_row_is_table_header", False)
        data = value["data"][1:] if has_header else value.get("data", [])
        for row_idx, row in enumerate(data, 1 if has_header else 0):
            tds = []
            for cell_idx, cell in enumerate(row):
                cell_key = (row_idx, cell_idx)
                if hidden.get(cell_key):
                    continue

                td = {"value": cell}
                if classname := classnames.get(cell_key):
                    td["tdClasses"] = classname
                if span := spans.get(cell_key):
                    td["span"] = span

                tds.append(td)

            trs.append({"tds": tds})
        return trs

    def clean(self, value):
        if not value or not value.get("table_header_choice"):
            raise ValidationError("Select an option for Table headers")

        data = value.get("data", [])
        all_cells_empty = all(not cell for row in data for cell in row)
        if all_cells_empty:
            raise ValidationError("The table cannot be empty")

        return super().clean(value)

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
                span = ""
                if merge["rowspan"] > 1:
                    span += f'rowspan="{merge["rowspan"]}" '
                if merge["colspan"] > 1:
                    span += f'colspan="{merge["colspan"]}" '

                if span:
                    spans[(merge["row"], merge["col"])] = mark_safe(span)  # noqa: S308

        return {
            "options": {
                "caption": value.get("table_caption"),
                "ths": self._get_header(value, hidden, spans),
                "trs": self._get_rows(value, classnames, hidden, spans),
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
