import uuid

from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.functional import classproperty
from django.utils.translation import gettext_lazy as _
from modelcluster.models import ClusterableModel
from wagtail import blocks
from wagtail.admin.panels import (
    FieldPanel,
    FieldRowPanel,
    MultiFieldPanel,
    ObjectList,
    TabbedInterface,
)
from wagtail.contrib.typed_table_block.blocks import TypedTableBlock
from wagtail.fields import StreamField
from wagtail.models import (
    DraftStateMixin,
    PreviewableMixin,
    RevisionMixin,
    SpecificMixin,
)

from ons_alpha.charts.admin_forms import BaseChartEditForm
from ons_alpha.charts.constants import AnnotationStyle, BarChartType, LegendPosition
from ons_alpha.charts.validators import csv_file_validator


class Chart(
    PreviewableMixin, DraftStateMixin, RevisionMixin, SpecificMixin, ClusterableModel
):
    base_form_class = BaseChartEditForm
    uuid = models.UUIDField(
        verbose_name=_("UUID"),
        default=uuid.uuid4,
        db_index=True,
        unique=True,
        editable=False,
    )
    name = models.CharField(
        verbose_name=_("name"),
        max_length=255,
        help_text=_(
            "The editor-facing name that will appear in the listing and chooser interfaces."
        ),
    )
    content_type = models.ForeignKey(
        ContentType,
        verbose_name=_("content type"),
        related_name="charts",
        on_delete=models.CASCADE,
    )
    content_type.wagtail_reference_index_ignore = True

    def __str__(self):
        return self.name


class BaseHighchartsChart(Chart):
    title = models.CharField(verbose_name=_("title"), max_length=255)
    subtitle = models.CharField(verbose_name=_("subtitle"), max_length=255, blank=True)
    show_legend = models.BooleanField(default=False)
    legend_position = models.CharField(
        max_length=6, choices=LegendPosition.choices, default=LegendPosition.TOP
    )

    x_label = models.CharField(verbose_name=_("label"), max_length=255)
    x_max = models.FloatField(verbose_name=_("scale cap (max)"), blank=True, null=True)
    x_min = models.FloatField(verbose_name=_("scale cap (min)"), blank=True, null=True)

    y_label = models.CharField(verbose_name=_("label"), max_length=255)
    y_max = models.FloatField(verbose_name=_("scale cap (max)"), blank=True, null=True)
    y_min = models.FloatField(verbose_name=_("scale cap (min)"), blank=True, null=True)

    data_file = models.FileField(
        verbose_name=_("CSV file"),
        upload_to="charts",
        max_length=500,
        blank=True,
        validators=[csv_file_validator],
    )
    data = StreamField(
        [
            (
                "table",
                TypedTableBlock(
                    [
                        ("text", blocks.CharBlock(max_length=200, label=_("Text"))),
                        ("number", blocks.IntegerBlock(label=_("Whole number"))),
                        ("float", blocks.FloatBlock(label=_("Floating point number"))),
                    ]
                ),
            )
        ],
        blank=True,
        null=True,
        max_num=1,
    )

    class Meta:
        abstract = True

    general_panels = [
        FieldPanel("name"),
        FieldPanel("data_source"),
        FieldPanel("data_file"),
        FieldPanel("data"),
    ]

    config_panels = [
        FieldPanel("title"),
        FieldPanel("subtitle"),
        MultiFieldPanel(
            heading=_("X axis"),
            children=[
                FieldPanel("x_label"),
                FieldRowPanel(
                    [
                        FieldPanel("x_min"),
                        FieldPanel("x_max"),
                    ]
                ),
            ],
        ),
        MultiFieldPanel(
            heading=_("Y axis"),
            children=[
                FieldPanel("y_label"),
                FieldRowPanel(
                    [
                        FieldPanel("y_min"),
                        FieldPanel("y_max"),
                    ]
                ),
            ],
        ),
        MultiFieldPanel(
            heading=_("Legend"),
            children=[
                FieldPanel("show_legend"),
                FieldPanel("legend_position"),
            ],
        ),
    ]

    def highcharts_chart_type(self):
        raise NotImplementedError

    @classproperty
    def edit_handler(cls):
        return TabbedInterface(
            [
                ObjectList(cls.general_panels, heading=_("Common")),
                ObjectList(cls.config_panels, heading=_("Options")),
            ]
        )


class LineChart(BaseHighchartsChart):
    template = "components/charts/line-chart.html"

    class Meta:
        verbose_name = _("line chart")
        verbose_name_plural = _("line charts")

    @classproperty
    def edit_handler(cls):
        return TabbedInterface(
            [
                ObjectList(cls.general_panels, heading=_("Common")),
                ObjectList(cls.config_panels, heading=_("Options")),
            ]
        )

    def highcharts_chart_type(self):
        return "line"


class BarChart(BaseHighchartsChart):
    template = "components/charts/bar-chart.html"

    subtype = models.CharField(
        max_length=20,
        verbose_name="sub-type",
        choices=BarChartType.choices,
        default=BarChartType.BAR,
    )

    class Meta:
        verbose_name = _("column or bar chart")
        verbose_name_plural = _("column or bar charts")

    def is_stacked(self) -> bool:
        return self.subtype in [
            BarChartType.STACKED_BAR.value,
            BarChartType.STACKED_COLUMN.value,
        ]

    def highcharts_chart_type(self):
        return self.subtype.split("_")[-1]

    config_panels = [FieldPanel("subtype")] + BaseHighchartsChart.config_panels
