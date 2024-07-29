from django.conf import settings
from django.forms import Media
from django.utils.functional import cached_property
from wagtail import blocks
from wagtail.blocks.field_block import FieldBlockAdapter
from wagtail.telepath import register


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
        ],
        default="warn",
    )
    body = blocks.RichTextBlock(features=settings.RICH_TEXT_BASIC)
    title = blocks.CharBlock(required=False, label="Title (optional)")

    class Meta:
        label = "Warning or information panel"
        template = "templates/components/streamfield/panel_block.html"


class PreviousVersionBlock(blocks.IntegerBlock):
    pass


class CorrectionBlock(blocks.StructBlock):
    when = blocks.DateTimeBlock()
    text = blocks.RichTextBlock(features=settings.RICH_TEXT_BASIC)
    previous_version = PreviousVersionBlock(required=False)

    class Meta:
        template = "templates/components/streamfield/corrections_block.html"
        help_text = "Warning: Reordering or deleting a correction will change its (and others') version number."


class PreviousVersionBlockAdapter(FieldBlockAdapter):
    js_constructor = "ons_alpha.core.blocks.panels.PreviousVersionBlock"

    @cached_property
    def media(self):
        structblock_media = super().media
        return Media(js=structblock_media._js + ["js/previous-version-block.js"], css=structblock_media._css)


register(PreviousVersionBlockAdapter(), PreviousVersionBlock)


class NoticeBlock(blocks.StructBlock):
    when = blocks.DateTimeBlock()
    text = blocks.RichTextBlock(features=settings.RICH_TEXT_BASIC)

    class Meta:
        template = "templates/components/streamfield/notices_block.html"
