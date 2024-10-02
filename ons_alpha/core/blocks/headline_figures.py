from django.utils.translation import gettext as _
from wagtail.blocks import (
    CharBlock,
    ListBlock,
    StructBlock,
)


class HeadlineFiguresItemBlock(StructBlock):
    title = CharBlock(label=_("Title"), max_length=60, required=True)
    figure = CharBlock(label=_("Figure"), max_length=10, required=True)
    supporting_text = CharBlock(label=_("Supporting text"), max_length=100, required=False)


class HeadlineFiguresBlock(ListBlock):
    def __init__(self, search_index=True, **kwargs):
        kwargs.setdefault("min_num", 3)
        kwargs.setdefault("max_num", 3)
        super().__init__(HeadlineFiguresItemBlock, search_index=search_index, **kwargs)

    class Meta:
        icon = "pick"
        label = _("Headline figures")
        template = "templates/components/streamfield/headline_figures_block.html"
