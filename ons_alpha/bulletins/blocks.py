from wagtail.blocks import ListBlock, RichTextBlock, StreamBlock
from wagtail.embeds.blocks import EmbedBlock
from wagtail.images.blocks import ImageChooserBlock

from ons_alpha.core.blocks import (
    CorrectionBlock,
    HeadingBlock,
    NoticeBlock,
    PanelBlock,
    TableBlock,
)


class BulletinStoryBlock(StreamBlock):
    heading = HeadingBlock(show_back_to_toc=True)
    rich_text = RichTextBlock()
    panel = PanelBlock()
    table = TableBlock()
    embed = EmbedBlock()
    image = ImageChooserBlock()


class CorrectionsNoticesStoryBlock(StreamBlock):
    corrections = ListBlock(CorrectionBlock(), template="templates/components/streamfield/corrections_block.html")
    notices = ListBlock(NoticeBlock(), template="templates/components/streamfield/notices_block.html")

    class Meta:
        block_counts = {"corrections": {"max_num": 1}, "notices": {"max_num": 1}}
        template = "templates/components/streamfield/corrections_notices_block.html"
