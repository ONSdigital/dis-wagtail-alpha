from wagtail import blocks
from wagtail.snippets.blocks import SnippetChooserBlock

from ons_alpha.charts.models import Chart


class ChartEmbedBlock(blocks.StructBlock):
    chart = SnippetChooserBlock(Chart)

    class Meta:
        template = "templates/components/streamfield/chart.html"

    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context)
        request = parent_context.get("request") if parent_context else None
        chart = value["chart"].specific
        context.update(chart.get_context(request))
        context["chart_template"] = chart.get_template(request)
        return context
