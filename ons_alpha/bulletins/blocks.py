from wagtail.blocks import ListBlock, RichTextBlock, StreamBlock
from wagtail.embeds.blocks import EmbedBlock
from wagtail.images.blocks import ImageChooserBlock
from wagtail.snippets.blocks import SnippetChooserBlock
from wagtailmath.blocks import MathBlock  #

from ons_alpha.core.blocks import (
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
    chart = SnippetChooserBlock("core.Chart", template="templates/components/streamfield/chart.html", icon="table")

    class Meta:
        block_counts = {"related_links": {"max_num": 1}}


class CorrectionsNoticesStoryBlock(StreamBlock):
    corrections = ListBlock(CorrectionBlock(), template="templates/components/streamfield/corrections_block.html")
    notices = ListBlock(NoticeBlock(), template="templates/components/streamfield/notices_block.html")

    class Meta:
        block_counts = {"corrections": {"max_num": 1}, "notices": {"max_num": 1}}
        template = "templates/components/streamfield/corrections_notices_block.html"
