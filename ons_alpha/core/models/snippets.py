from django.db import models
from wagtail import blocks
from wagtail.admin.panels import FieldPanel
from wagtail.fields import RichTextField
from wagtail.models import PreviewableMixin
from wagtail.search import index
from wagtail.snippets.models import register_snippet
from wagtailcharts.blocks import ChartBlock

from ons_alpha.utils.fields import StreamField


__all__ = ["CallToActionSnippet", "ContactDetails"]


@register_snippet
class CallToActionSnippet(models.Model):
    title = models.CharField(max_length=255)
    summary = RichTextField(blank=True, max_length=255)
    image = models.ForeignKey(
        "images.CustomImage",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    link = StreamField(
        blocks.StreamBlock(
            [
                (
                    "external_link",
                    blocks.StructBlock(
                        [("url", blocks.URLBlock()), ("title", blocks.CharBlock())],
                        icon="link",
                    ),
                ),
                (
                    "internal_link",
                    blocks.StructBlock(
                        [
                            ("page", blocks.PageChooserBlock()),
                            ("title", blocks.CharBlock(required=False)),
                        ],
                        icon="link",
                    ),
                ),
            ],
            max_num=1,
        ),
        use_json_field=True,
    )

    panels = [
        FieldPanel("title"),
        FieldPanel("summary"),
        FieldPanel("image"),
        FieldPanel("link"),
    ]

    def __str__(self):  # pylint: disable=invalid-str-returned
        return self.title

    def get_link_text(self):
        # Link is required, so we should always have
        # an element with index 0
        block = self.link[0]

        title = block.value["title"]
        if block.block_type == "external_link":
            return title

        # Title is optional for internal_link
        # so fallback to page's title, if it's empty
        return title or block.value["page"].title

    def get_link_url(self):
        # Link is required, so we should always have
        # an element with index 0
        block = self.link[0]

        if block.block_type == "external_link":
            return block.value["url"]

        return block.value["page"].get_url()


@register_snippet
class ContactDetails(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=255, blank=True)

    panels = [
        FieldPanel("name"),
        FieldPanel("email"),
        FieldPanel("phone"),
    ]

    class Meta:
        verbose_name_plural = "contact details"

    def __str__(self):
        return str(self.name)


@register_snippet
class Chart(index.Indexed, PreviewableMixin, models.Model):
    chart = StreamField([("chart", ChartBlock())], use_json_field=True, min_num=1, max_num=1)

    panels = [FieldPanel("chart")]

    search_fields = [index.SearchField("title")]

    def __str__(self):
        return str(self.title)

    @property
    def title(self):
        try:
            return self.chart[0].value["title"]
        except IndexError:
            return ""

    def get_preview_template(self, request, mode_name):
        return "templates/snippets/chart.html"
