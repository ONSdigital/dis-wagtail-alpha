from wagtail.blocks import CharBlock, ListBlock, RichTextBlock, StructBlock


class AccordionSectionBlock(StructBlock):
    title = CharBlock(max_length=200)
    content = RichTextBlock(features=["bold", "italic", "link", "ol", "ul"])

    class Meta:
        label = "Sections"
        icon = "title"


class AccordionBlock(StructBlock):
    sections = ListBlock(
        AccordionSectionBlock(),
    )

    class Meta:
        label = "Accordion"
        icon = "list-ol"
        template = "templates/components/streamfield/accordion_block.html"

    def get_context(self, value, parent_context=None):
        ctx = super().get_context(value, parent_context=parent_context)
        ctx["accordions"] = [
            {
                "title": section["title"],
                "content": section["content"],
            }
            for section in value["sections"]
        ]
        return ctx
