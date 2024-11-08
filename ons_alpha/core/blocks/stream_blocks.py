from wagtail.blocks import RichTextBlock, StreamBlock
from wagtail.embeds.blocks import EmbedBlock
from wagtail.images.blocks import ImageChooserBlock
from wagtailmath.blocks import MathBlock

from ons_alpha.core.blocks import (
    ButtonLinkBlock,
    CorrectionBlock,
    DocumentListBlock,
    DocumentsBlock,
    HeadingBlock,
    NoticeBlock,
    ONSChartEmbedBlock,
    ONSEmbedBlock,
    ONSTableBlock,
    PanelBlock,
    RelatedContentBlock,
    RelatedLinksBlock,
)
from ons_alpha.core.blocks import TableBlock as OldTableBlock


class SimpleStoryBlock(StreamBlock):
    heading = HeadingBlock()
    rich_text = RichTextBlock()
    panel = PanelBlock()
    document_list = DocumentListBlock()
    button_link = ButtonLinkBlock()

    class Meta:
        template = "templates/components/streamfield/stream_block.html"


class CoreStoryBlock(StreamBlock):
    heading = HeadingBlock()
    rich_text = RichTextBlock()
    panel = PanelBlock()
    embed = EmbedBlock()
    image = ImageChooserBlock()
    documents = DocumentsBlock()
    related_links = RelatedLinksBlock(RelatedContentBlock())
    ons_table = ONSTableBlock(group="DataVis")
    ons_chart_embed = ONSChartEmbedBlock(group="DataVis", label="ONS Chart Embed")
    ons_embed = ONSEmbedBlock(group="DataVis", label="ONS General Embed")
    equation = MathBlock(icon="decimal", group="DataVis")
    table = OldTableBlock(
        group="DataVis",
        help_text="This is a basic table-only block provided by Wagtail. "
        "Use the 'ONS Table' block for the full ONS needs.",
    )
    document_list = DocumentListBlock()

    class Meta:
        block_counts = {"related_links": {"max_num": 1}}
        template = "templates/components/streamfield/stream_block.html"


class CorrectionsNoticesStoryBlock(StreamBlock):
    correction = CorrectionBlock()
    notice = NoticeBlock()

    class Meta:
        template = "templates/components/streamfield/corrections_notices_block.html"
