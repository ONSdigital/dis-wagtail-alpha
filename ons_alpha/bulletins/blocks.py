from wagtail.blocks import RichTextBlock, StreamBlock
from wagtail.embeds.blocks import EmbedBlock
from wagtail.images.blocks import ImageChooserBlock

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
    embed = EmbedBlock()
    image = ImageChooserBlock()
