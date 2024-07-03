from wagtail import blocks
from wagtail.embeds.blocks import EmbedBlock
from wagtail.snippets.blocks import SnippetChooserBlock

from ons_alpha.core.blocks import DocumentBlock, HeadingBlock, ImageBlock, QuoteBlock, TableBlock, TypedTableBlock


class StoryBlock(blocks.StreamBlock):
    """
    Main StreamField block to be inherited by Pages
    """

    heading = HeadingBlock()
    paragraph = blocks.RichTextBlock()
    image = ImageBlock()
    quote = QuoteBlock()
    embed = EmbedBlock()
    call_to_action = SnippetChooserBlock(
        "core.CallToActionSnippet",
        template="templates/components/streamfield/call_to_action_block.html",
    )
    document = DocumentBlock()
    table = TableBlock()
    typed_table = TypedTableBlock(label="Rich text and numeric table block")
