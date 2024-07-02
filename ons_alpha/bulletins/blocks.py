from wagtail.blocks import RichTextBlock, StreamBlock

from ons_alpha.core.blocks import (
    HeadingBlock,
    PanelBlock,
    TableBlock,
)


class BulletinStoryBlock(StreamBlock):
    heading = HeadingBlock()
    rich_text = RichTextBlock()
    panel = PanelBlock()
    table = TableBlock()
