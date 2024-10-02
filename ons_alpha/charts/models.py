import csv
import uuid

from collections.abc import Sequence
from typing import Any

from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db import models
from django.http import HttpRequest
from django.urls import reverse
from django.utils.functional import cached_property, classproperty
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
from wagtail.contrib.typed_table_block.blocks import TypedTable, TypedTableBlock
from wagtail.fields import StreamField
from wagtail.models import (
    DraftStateMixin,
    PreviewableMixin,
    RevisionMixin,
    SpecificMixin,
)

from ons_alpha.private_media.models import PrivateMediaCollectionMember
from ons_alpha.charts.constants import BarChartType, DataSource, LegendPosition
from ons_alpha.charts.validators import csv_file_validator


class Chart(
    PreviewableMixin,
    DraftStateMixin,
    RevisionMixin,
    SpecificMixin,
    PrivateMediaCollectionMember,
    ClusterableModel,
):
    template: str | None = None
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.id and not self.content_type_id:
            # this model is being newly created
            # rather than retrieved from the db;

            # set content type to correctly represent the model class
            # that this was created as
            self.content_type = ContentType.objects.get_for_model(self)

    def get_template(self, request, **kwargs) -> str:
        if self.template is None:
            raise ValueError(
                f"{type(self).__name__}.template is None and the get_template() method has not been overridden."
            )
        return self.template

    def get_preview_template(self, request, preview_mode: str, **kwargs):
        return self.get_template(request, preview_mode=preview_mode, **kwargs)

    def get_context(self, request, **kwargs):
        context = {
            "chart": self.specific,
            "chart_type": self.specific_class,
        }
        context.update(kwargs)
        return context

    def get_preview_context(self, request, preview_mode: str, **kwargs):
        return self.get_context(request, preview_mode=preview_mode, **kwargs)

    def get_privacy_controlled_files(self):
        return []

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

    data_source = models.CharField(
        max_length=10, choices=DataSource.choices, default=DataSource.CSV
    )
    data_file = models.FileField(
        verbose_name=_("CSV file"),
        upload_to="charts",
        max_length=500,
        blank=True,
        validators=[csv_file_validator],
    )
    data_manual = StreamField(
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
        verbose_name=_("data"),
        blank=True,
        null=True,
        max_num=1,
    )

    class Meta:
        abstract = True

    def get_privacy_controlled_files(self):
        files = []
        if self.data_file:
            files.append(self.data_file)
        return files

    def clean(self):
        super().clean()
        if self.data_source == DataSource.CSV and not self.data_file:
            raise ValidationError({"data_file": _("This field is required")})
        if self.data_source == DataSource.MANUAL and not self.data_manual:
            raise ValidationError({"data_manual": _("This field is required")})

    def get_context(self, request, **kwargs) -> dict[str, Any]:
        context = {}
        if self.include_data_in_context(request):
            context["data"] = self.get_data_json(request)
        else:
            context["data_url"] = self.get_data_url()
        context.update(**kwargs)
        return super().get_context(request, **context)

    def include_data_in_context(self, request) -> bool:
        """
        Return a `bool` indicating whether the chart should be rendered with the data available
        in the template context. If `True` value indicates that data should be used to render the
        chart directly. A `False` value indicates that data should be loaded dynamically, by making
        a separate HTTP request to the 'retrieve_data' API endpoint for this chart.

        Always returns `True` when previewing a chart, or the chart has not yet been published.
        This is required to allow changes to the data to be reflected in previews, and to get
        around the fact that the 'retrieve_data' API endpoint only works for published charts, and
        only surfaces the most recently-published data.
        """
        if not self.live or getattr(request, "is_preview", False):
            return True
        # Only use the data API for published charts, where the data was added manually,
        # or the uploaded CSV is below 1.5M.
        return self.data_source == DataSource.MANUAL or (
            self.data_source == DataSource.CSV and self.data_file.size <= 1572864
        )

    def get_data_json(self, request: HttpRequest) -> dict[str, list]:
        """
        Return a JSON-serializable representation of the chart's data. Used by both:

        * `get_context()` (when including chart data directly in the template context)
        * `ChartAPIViewSet.retrieve_data()` (when serving live data via the API)
        """
        if self.data_source == DataSource.MANUAL and self.data_manual:
            return {
                "columns": [col["heading"] for col in self.manual_data_table.columns],
                "rows": self.manual_data_table.row_data,
            }

        columns = []
        rows = []
        if self.data_source == DataSource.CSV and self.data_file:
            with open(self.data_file, "+r", newline="") as csvfile:
                reader = csv.reader(csvfile)
                for i, row in enumerate(reader):
                    if not i:
                        columns = row
                    else:
                        rows.append(row)
            return {
                "columns": columns,
                "rows": rows,
            }
        return {}

    @cached_property
    def data_headers(self) -> Sequence[str]:
        if self.data_source == DataSource.CSV and self.data_file:
            with open(self.data_file, "+r", newline="") as csvfile:
                reader = csv.DictReader(csvfile)
                return reader.fieldnames or []
        if self.data_source == DataSource.MANUAL and self.data_manual:
            return [col["heading"] for col in self.manual_data_table.columns]
        return []

    @property
    def manual_data_table(self) -> TypedTable:
        return self.data_manual[0].value

    def get_data_url(self) -> str:
        return reverse("chart-data-csv", args=[self.uuid])

    general_panels = [
        FieldPanel("name"),
        FieldPanel("collection"),
        FieldPanel("data_source"),
        FieldPanel("data_file"),
        FieldPanel("data_manual"),
    ]

    settings_panels = [
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
                ObjectList(cls.settings_panels, heading=_("Chart configuration")),
            ]
        )


class LineChart(BaseHighchartsChart):
    template = "templates/components/charts/line_chart.html"

    class Meta:
        verbose_name = _("line chart")
        verbose_name_plural = _("line charts")

    def highcharts_chart_type(self):
        return "line"


class BarChart(BaseHighchartsChart):
    template = "templates/components/charts/bar_chart.html"

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

    settings_panels = [FieldPanel("subtype")] + BaseHighchartsChart.settings_panels
