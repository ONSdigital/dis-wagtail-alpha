from wagtail.blocks import RichTextBlock, StreamBlock
from wagtail.embeds.blocks import EmbedBlock
from wagtail.images.blocks import ImageChooserBlock
from wagtailmath.blocks import MathBlock

from ons_alpha.core.blocks import (
    ChartChooserBlock,
    CorrectionBlock,
    HeadingBlock,
    NoticeBlock,
    ONSEmbedBlock,
    PanelBlock,
    RelatedContentBlock,
    RelatedLinksBlock,
    TableBlock,
)


class BulletinStoryBlock(StreamBlock):
    heading = HeadingBlock(show_back_to_toc=False)
    rich_text = RichTextBlock()
    panel = PanelBlock()
    table = TableBlock(group="DataVis")
    equation = MathBlock(icon="decimal", group="DataVis")
    ons_embed = ONSEmbedBlock(group="DataVis")
    embed = EmbedBlock()
    image = ImageChooserBlock()
    related_links = RelatedLinksBlock(RelatedContentBlock())
    chart = ChartChooserBlock(group="DataVis")

    class Meta:
        block_counts = {"related_links": {"max_num": 1}}


class CorrectionsNoticesStoryBlock(StreamBlock):
    correction = CorrectionBlock()
    notice = NoticeBlock()

    class Meta:
        template = "templates/components/streamfield/corrections_notices_block.html"
