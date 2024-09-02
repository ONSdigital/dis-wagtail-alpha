from django.conf import settings
from wagtail.blocks import CharBlock, RichTextBlock, StreamBlock, StructBlock
from wagtail.embeds.blocks import EmbedBlock
from wagtail.images.blocks import ImageChooserBlock
from wagtailmath.blocks import MathBlock

# Import specific blocks to avoid circular dependency
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
    TableBlock as CustomTableBlock,  # Ensure we're using the custom TableBlock from core.blocks
)


# StructBlock for ONS Table
class ONSTableBlock(StructBlock):
    heading = CharBlock(required=True, help_text="Add a heading for the table.")
    table = CustomTableBlock(required=True, help_text="Add the table data here.")  # Use the correct TableBlock
    source = CharBlock(required=False, help_text="Add the source of the table data if applicable.")
    footnotes = RichTextBlock(
        features=settings.RICH_TEXT_BASIC, required=False, help_text="Add any footnotes for the table."
    )

    class Meta:
        template = "templates/components/streamfield/ons_table_block.html"
        icon = "table"
        label = "ONS Table"


# Core story block with added ONSTableBlock
class CoreStoryBlock(StreamBlock):
    heading = HeadingBlock()
    rich_text = RichTextBlock()
    panel = PanelBlock()
    embed = EmbedBlock()
    image = ImageChooserBlock()
    documents = DocumentsBlock()
    related_links = RelatedLinksBlock(RelatedContentBlock())
    table = CustomTableBlock(group="DataVis")  # Use the custom TableBlock from core.blocks
    ons_table = ONSTableBlock(group="DataVis")  # New block added
    equation = MathBlock(icon="decimal", group="DataVis")
    ons_embed = ONSEmbedBlock(group="DataVis", label="ONS Embed")
    chart = ChartChooserBlock(group="DataVis")

    class Meta:
        block_counts = {"related_links": {"max_num": 1}}


# Block for corrections and notices
class CorrectionsNoticesStoryBlock(StreamBlock):
    correction = CorrectionBlock()
    notice = NoticeBlock()

    class Meta:
        template = "templates/components/streamfield/corrections_notices_block.html"
