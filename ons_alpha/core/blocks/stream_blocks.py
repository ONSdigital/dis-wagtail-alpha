from wagtail.blocks import RichTextBlock, StreamBlock
from wagtail.embeds.blocks import EmbedBlock
from wagtail.images.blocks import ImageChooserBlock
from wagtailmath.blocks import MathBlock

from ons_alpha.core.blocks import (
    ChartChooserBlock,
    CorrectionBlock,
    DocumentsBlock,
    HeadingBlock,
    NoticeBlock,
    ONSEmbedBlock,
    PanelBlock,
    RelatedContentBlock,
    RelatedLinksBlock,
)
from ons_alpha.core.blocks import (
    TableBlock as OldTableBlock,  # Retain this for other usages in stream_blocks
)
from ons_alpha.core.blocks.markup import ONSTableBlock  # Import the relocated ONSTableBlock


class CoreStoryBlock(StreamBlock):
    heading = HeadingBlock()
    rich_text = RichTextBlock()
    panel = PanelBlock()
    embed = EmbedBlock()
    image = ImageChooserBlock()
    documents = DocumentsBlock()
    related_links = RelatedLinksBlock(RelatedContentBlock())
    table = OldTableBlock(group="DataVis")  # Retain the old table block for existing data
    ons_table = ONSTableBlock(group="DataVis")  # New block added
    equation = MathBlock(icon="decimal", group="DataVis")
    ons_embed = ONSEmbedBlock(group="DataVis", label="ONS Embed")
    chart = ChartChooserBlock(group="DataVis")

    class Meta:
        block_counts = {"related_links": {"max_num": 1}}


class CorrectionsNoticesStoryBlock(StreamBlock):
    correction = CorrectionBlock()
    notice = NoticeBlock()

    class Meta:
        template = "templates/components/streamfield/corrections_notices_block.html"
