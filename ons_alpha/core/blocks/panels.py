from django.conf import settings
from wagtail import blocks


class PanelBlock(blocks.StructBlock):
    variant = blocks.ChoiceBlock(
        choices=[
            ("announcement", "Announcement"),
            ("bare", "Bare"),
            ("branded", "Branded"),
            ("error", "Error"),
            ("ghost", "Ghost"),
            ("success", "Success"),
            ("warn-branded", "Warn (branded)"),
            ("warn", "Warn"),
        ]
    )
    title = blocks.CharBlock(required=False)
    body = blocks.RichTextBlock(features=settings.RICH_TEXT_BASIC)

    class Meta:
        template = "templates/components/streamfield/panel_block.html"


class CorrectionBlock(blocks.StructBlock):
    when = blocks.DateTimeBlock()
    text = blocks.RichTextBlock(features=settings.RICH_TEXT_BASIC)
    previous_version = ...


class NoticeBlock(blocks.StructBlock):
    when = blocks.DateTimeBlock()
    text = blocks.RichTextBlock(features=settings.RICH_TEXT_BASIC)
