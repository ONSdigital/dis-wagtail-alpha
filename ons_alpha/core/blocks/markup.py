from wagtail import blocks


class HeadingBlock(blocks.CharBlock):
    class Meta:
        template = "templates/components/streamfield/heading_block.html"
