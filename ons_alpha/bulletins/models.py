from wagtail.admin.panels import FieldPanel
from wagtail.blocks import RichTextBlock

from ons_alpha.core.blocks import HeadingBlock, PanelBlock
from ons_alpha.core.models.base import BasePage
from ons_alpha.utils.fields import StreamField


class BulletinPage(BasePage):
    template = "templates/pages/bulletins/bulletin_page.html"
    parent_page_types = ["topics.TopicPage"]

    body = StreamField(
        [
            ("heading", HeadingBlock()),
            ("rich_text", RichTextBlock()),
            ("panel", PanelBlock()),
        ],
        use_json_field=True,
    )

    content_panels = BasePage.content_panels + [FieldPanel("body")]
