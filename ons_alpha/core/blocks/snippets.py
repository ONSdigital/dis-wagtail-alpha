from wagtail.snippets.blocks import SnippetChooserBlock

from ons_alpha.core.models.snippets import Chart


class ChartChooserBlock(SnippetChooserBlock):
    def __init__(self, **kwargs):
        super().__init__(target_model=Chart, **kwargs)

    class Meta:
        template = "templates/components/streamfield/chart.html"
