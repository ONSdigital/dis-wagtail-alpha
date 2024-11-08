from django.forms.widgets import Media
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from wagtail import blocks
from wagtail.snippets.blocks import SnippetChooserBlock
from wagtail.telepath import register
from wagtailtables.blocks import TableAdapter, TableBlock


class SimpleTableBlock(TableBlock):
    table_data = blocks.TextBlock(label=_("Data"), default="[]")
    caption = None
    header_row = None
    header_col = None


class SimpleTableBlockAdapter(TableAdapter):
    def js_args(self, block):
        result = super().js_args(block)
        # We override wagtailtables js to remove the toolbar, as formatting
        # options are irrelevant to our data-only tables.
        result[2].pop("toolbar", None)
        return result

    @cached_property
    def media(self):
        # wagtailtables css doen't resize the widget container correctly, so we
        # need to add custom css to fix it.
        return super().media + Media(css={"all": ["wagtailtables/css/table-dataset.css"]})


register(SimpleTableBlockAdapter(), SimpleTableBlock)


class ChartEmbedBlock(blocks.StructBlock):
    chart = SnippetChooserBlock("charts.Chart")
    title = blocks.CharBlock(label=_("Title"))
    subtitle = blocks.CharBlock(label=_("Subtitle"))

    class Meta:
        template = "templates/components/streamfield/chart.html"

    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context)
        request = parent_context.get("request") if parent_context else None
        chart = value["chart"].specific

        # Override the title and subtitle
        chart.title = value["title"]
        chart.subtitle = value["subtitle"]

        # Add the chart context and template to allow the chart to be rendered
        context.update(chart.get_context(request))
        context["chart_template"] = chart.get_template(request)
        return context
