from django.utils.translation import gettext as _
from wagtail.blocks import (
    CharBlock,
    PageChooserBlock,
    StructBlock,
)


class ButtonLinkBlock(StructBlock):
    text = CharBlock(label=_("Text"), default="Get started", max_length=100, required=True)
    target_page = PageChooserBlock(label=_("Target page"), required=True)

    class Meta:
        template = "templates/components/streamfield/button_link_block.html"
        icon = "link"
        label = _("Button link")

    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context)
        request = parent_context.get("request") if parent_context else None
        context["text"] = value["text"]
        context["url"] = value["target_page"].get_url(request)
        return context
