from django.conf import settings  # Import settings to be used in RichTextBlock
from wagtail.blocks import CharBlock, RichTextBlock, StreamBlock, StructBlock
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
    TableBlock as OldTableBlock,  # Use the TableBlock from ons_alpha.core.blocks
)


class ONSTableBlock(StructBlock):
    heading = CharBlock(required=True, help_text="Add a heading for the table.")
    table = OldTableBlock(required=True, help_text="Add the table data here.")
    source = CharBlock(required=False, help_text="Add the source of the table data if applicable.")
    footnotes = RichTextBlock(
        features=settings.RICH_TEXT_BASIC, required=False, help_text="Add any footnotes for the table."
    )

    class Meta:
        template = "templates/components/streamfield/ons_table_block.html"
        icon = "table"
        label = "ONS Table"


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
