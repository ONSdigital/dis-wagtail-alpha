from wagtail.blocks import RichTextBlock, StreamBlock
from wagtail.embeds.blocks import EmbedBlock
from wagtail.images.blocks import ImageChooserBlock
from wagtailmath.blocks import MathBlock

from ons_alpha.core.blocks import (
    ChartChooserBlock,
    HeadingBlock,
    ONSEmbedBlock,
    PanelBlock,
    RelatedContentBlock,
    RelatedLinksBlock,
    TableBlock,
)


class CoreStoryBlock(StreamBlock):
    heading = HeadingBlock()
    rich_text = RichTextBlock()
    panel = PanelBlock()
    embed = EmbedBlock()
    image = ImageChooserBlock()
    related_links = RelatedLinksBlock(RelatedContentBlock())
    table = TableBlock(group="DataVis")
    equation = MathBlock(icon="decimal", group="DataVis")
    ons_embed = ONSEmbedBlock(group="DataVis", label="ONS Embed")
    chart = ChartChooserBlock(group="DataVis")

    class Meta:
        block_counts = {"related_links": {"max_num": 1}}
