from django.utils.text import slugify
from wagtail import blocks


class HeadingBlock(blocks.CharBlock):
    class Meta:
        template = "templates/components/streamfield/heading_block.html"

    def to_table_of_contents_items(self, value):
        return [{"url": "#" + slugify(value), "text": value}]
