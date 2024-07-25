from wagtail.blocks import StreamBlock

from ons_alpha.core.blocks import CorrectionBlock, NoticeBlock


class CorrectionsNoticesStoryBlock(StreamBlock):
    correction = CorrectionBlock()
    notice = NoticeBlock()

    class Meta:
        template = "templates/components/streamfield/corrections_notices_block.html"
