from django.utils.text import slugify
from wagtail import blocks

from ons_alpha.core.blocks import RelatedContentBlock


class ContentSectionBlock(blocks.StructBlock):
    title = blocks.CharBlock()
    links = blocks.ListBlock(RelatedContentBlock())

    class Meta:
        template = "templates/components/streamfield/release_content_section.html"

    def to_table_of_contents_items(self, value):
        return [{"url": "#" + slugify(value["title"]), "text": value["title"]}]


class ReleaseStoryBlock(blocks.StreamBlock):
    release_content = ContentSectionBlock()
