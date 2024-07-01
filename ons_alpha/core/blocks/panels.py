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
    body = blocks.RichTextBlock()

    class Meta:
        template = "templates/components/streamfield/panel_block.html"
