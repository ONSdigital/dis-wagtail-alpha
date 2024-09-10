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
    ONSTableBlock,
    PanelBlock,
    RelatedContentBlock,
    RelatedLinksBlock,
)
from ons_alpha.core.blocks import TableBlock as OldTableBlock


class CoreStoryBlock(StreamBlock):
    heading = HeadingBlock()
    rich_text = RichTextBlock()
    panel = PanelBlock()
    embed = EmbedBlock()
    image = ImageChooserBlock()
    documents = DocumentsBlock()
    related_links = RelatedLinksBlock(RelatedContentBlock())
    ons_table = ONSTableBlock(group="DataVis")
    ons_embed = ONSEmbedBlock(group="DataVis", label="ONS Embed")
    chart = ChartChooserBlock(group="DataVis")
    equation = MathBlock(icon="decimal", group="DataVis")
    table = OldTableBlock(
        group="DataVis",
        help_text="This is a basic table-only block provided by Wagtail. "
        "Use the 'ONS Table' block for the full ONS needs.",
    )

    class Meta:
        block_counts = {"related_links": {"max_num": 1}}


class CorrectionsNoticesStoryBlock(StreamBlock):
    correction = CorrectionBlock()
    notice = NoticeBlock()

    class Meta:
        template = "templates/components/streamfield/corrections_notices_block.html"
