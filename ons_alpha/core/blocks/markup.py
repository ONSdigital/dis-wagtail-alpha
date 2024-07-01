from django.utils.text import slugify
from wagtail import blocks
from wagtail.contrib.table_block.blocks import TableBlock as WagtailTableBlock


class HeadingBlock(blocks.CharBlock):
    class Meta:
        template = "templates/components/streamfield/heading_block.html"

    def to_table_of_contents_items(self, value):
        return [{"url": "#" + slugify(value), "text": value}]


class TableBlock(WagtailTableBlock):
    class Meta:
        template = "templates/components/streamfield/table_block.html"

    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context)  #

        table_header = (
            [{"value": cell} for cell in value["data"][0]]
            if value.get("data", None)
            and len(value["data"]) > 0
            and value.get("first_row_is_table_header", False)
            else []
        )

        return {
            "options": {
                "caption": value.get("table_caption"),
                "ths": table_header,
                "trs": [
                    {"tds": [{"value": cell} for cell in row]}
                    for row in (
                        value["data"][1:] if table_header else value.get("data", [])
                    )
                ],
            },
            **context,
        }

    def render(self, value, context=None):
        # TableBlock has a very custom `render` method. We don't want that
        return super(blocks.FieldBlock, self).render(value, context)
