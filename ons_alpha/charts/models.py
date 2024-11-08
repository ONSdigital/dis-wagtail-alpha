import csv
import io
import json
import uuid

from collections.abc import Sequence
from contextlib import contextmanager
from typing import Any

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.utils.functional import cached_property, classproperty
from django.utils.translation import gettext_lazy as _
from modelcluster.models import ClusterableModel
from wagtail.admin.panels import (
    FieldPanel,
    FieldRowPanel,
    MultiFieldPanel,
    ObjectList,
    TabbedInterface,
)
from wagtail.fields import RichTextField, StreamField
from wagtail.models import (
    DraftStateMixin,
    PreviewableMixin,
    RevisionMixin,
    SpecificMixin,
)
from wagtail.permission_policies import ModelPermissionPolicy
from wagtail.rich_text import expand_db_html

from ons_alpha.charts.blocks import SimpleTableBlock
from ons_alpha.charts.constants import (
    HIGHCHARTS_THEMES,
    AxisValueType,
    BarChartType,
    DataSource,
    HighchartsTheme,
    LegendPosition,
)
from ons_alpha.charts.validators import csv_file_validator
from ons_alpha.utils.fields import NonStrippingCharField


class Chart(
    PreviewableMixin,
    DraftStateMixin,
    RevisionMixin,
    SpecificMixin,
    ClusterableModel,
):
    preview_template = "templates/components/charts/preview.html"
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
        help_text=_("The editor-facing name that will appear in the listing and chooser interfaces."),
    )
    content_type = models.ForeignKey(
        ContentType,
        verbose_name=_("content type"),
        related_name="charts",
        on_delete=models.CASCADE,
    )
    content_type.wagtail_reference_index_ignore = True

    title = models.CharField(verbose_name=_("title"), max_length=255, blank=True)
    subtitle = models.CharField(verbose_name=_("subtitle"), max_length=255, blank=True)
    caption = RichTextField(
        verbose_name=_("caption"),
        blank=True,
        features=settings.RICH_TEXT_BASIC,
        default="Source: Office for National Statistics",
    )

    @classproperty
    def permission_policy(cls):  # pylint: disable=no-self-argument
        return ModelPermissionPolicy(cls)

    def __str__(self):
        return str(self.name)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.id and not self.content_type_id:
            # this model is being newly created
            # rather than retrieved from the db;

            # set content type to correctly represent the model class
            # that this was created as
            self.content_type = ContentType.objects.get_for_model(self)

    def get_template(self, request, **kwargs) -> str:  # pylint: disable=unused-argument
        if self.template is None:
            raise ValueError(
                f"{type(self).__name__}.template is None and the get_template() method has not been overridden."
            )
        return self.template

    def get_context(self, request, **kwargs):  # pylint: disable=unused-argument
        context = {
            "chart": self.specific,
            "chart_type": self.specific_class,
        }
        context.update(kwargs)
        return context

    def get_preview_template(self, request, mode_name: str, **kwargs) -> str:  # pylint: disable=unused-argument
        return self.preview_template

    def get_preview_context(self, request, mode_name: str, **kwargs) -> dict[str, Any]:
        return self.get_context(request, is_preview=True, **kwargs)


class BaseHighchartsChart(Chart):
    show_legend = models.BooleanField(verbose_name=_("show legend?"), default=False)
    legend_position = models.CharField(
        verbose_name=_("label position"),
        max_length=6,
        choices=LegendPosition.choices,
        default=LegendPosition.TOP,
    )
    show_value_labels = models.BooleanField(verbose_name=_("show value labels?"), default=False)
    theme = models.CharField(
        verbose_name=_("theme"),
        max_length=10,
        choices=HighchartsTheme.choices,
        default=HighchartsTheme.PRIMARY,
    )
    height = models.IntegerField(verbose_name=_("height"), default=400)

    x_label = models.CharField(verbose_name=_("label"), max_length=255, blank=True)
    x_type = models.CharField(
        verbose_name=_("value type"),
        max_length=10,
        choices=AxisValueType.choices,
        default=AxisValueType.TEXT,
    )
    x_max = models.FloatField(verbose_name=_("scale cap (max)"), blank=True, null=True)
    x_min = models.FloatField(verbose_name=_("scale cap (min)"), blank=True, null=True)
    x_reversed = models.BooleanField(verbose_name=_("reverse axis?"), default=False)
    x_tick_interval = models.FloatField(verbose_name=_("tick interval"), blank=True, null=True)

    y_label = models.CharField(verbose_name=_("label"), max_length=255, blank=True)
    y_type = models.CharField(
        verbose_name=_("value type"),
        max_length=10,
        choices=AxisValueType.choices,
        default=AxisValueType.NUMBER,
    )
    y_max = models.FloatField(verbose_name=_("scale cap (max)"), blank=True, null=True)
    y_min = models.FloatField(verbose_name=_("scale cap (min)"), blank=True, null=True)
    y_value_suffix = NonStrippingCharField(verbose_name=_("value suffix (optional)"), max_length=30, blank=True)
    y_tooltip_suffix = NonStrippingCharField(
        verbose_name=_("tooltip value suffix (optional)"), max_length=30, blank=True
    )
    y_reversed = models.BooleanField(verbose_name=_("reverse axis?"), default=False)
    y_tick_interval = models.FloatField(verbose_name=_("tick interval"), blank=True, null=True)

    data_source = models.CharField(
        verbose_name=_("data source"),
        max_length=10,
        choices=DataSource.choices,
        default=DataSource.CSV,
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
                SimpleTableBlock(label=_("Table")),
            )
        ],
        verbose_name=_("data"),
        blank=True,
        null=True,
        max_num=1,
    )

    class Meta:
        abstract = True

    def clean(self):
        super().clean()
        if self.data_source == DataSource.CSV and not self.data_file:
            raise ValidationError({"data_file": _("This field is required")})
        if self.data_source == DataSource.MANUAL and not self.data_manual:
            raise ValidationError({"data_manual": _("This field is required")})

    def get_context(self, request, **kwargs) -> dict[str, Any]:
        row_data = (
            self.rows if self.include_data_in_context(request, is_preview=kwargs.get("is_preview", False)) else None
        )
        highcharts_config = self.get_highcharts_config(row_data)
        return super().get_context(request, highcharts_config=highcharts_config, **kwargs)

    def include_data_in_context(self, request, *, is_preview: bool = False) -> bool:  # pylint: disable=unused-argument
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
        # Only use the data API for published charts, where the data was added manually
        return is_preview or self.data_source == DataSource.MANUAL

    @contextmanager
    def read_csv(self) -> csv.reader:
        try:
            csvfile = self.data_file.open("rb")
            textwrapper = io.TextIOWrapper(csvfile, encoding="utf-8", newline="")
            textwrapper.seek(0)
            reader = csv.reader(textwrapper)
            yield reader
        finally:
            csvfile.close()

    @cached_property
    def manual_data_rows(self):
        data_json = json.loads(self.data_manual[0].value["table_data"])
        print(data_json)
        return data_json["data"]

    @cached_property
    def rows(self) -> dict[str, list]:
        """
        Return a JSON-serializable representation of the chart's row data. Used by both:

        * `get_context()` (when including chart data directly in the template context)
        * `ChartAPIViewSet.retrieve_data()` (when serving live data via the API)
        """
        if self.data_source == DataSource.MANUAL and self.data_manual:
            return self.manual_data_rows[1:]

        if self.data_source == DataSource.CSV and self.data_file:
            headers = []
            rows = []
            with self.read_csv() as reader:
                for i, row in enumerate(reader):
                    if not i:
                        headers = row
                    else:
                        rows.append(row)
                # Set the 'headers' cached_property whilst the file is open
                self.headers = headers
            return rows
        return []

    @cached_property
    def headers(self) -> Sequence[str]:  # pylint: disable=method-hidden
        if self.data_source == DataSource.MANUAL and self.data_manual:
            return self.manual_data_rows[0]

        if self.data_source == DataSource.CSV and self.data_file:
            with self.read_csv() as reader:
                # 'fieldnames' is only available after the first row has been read
                next(reader)
                return reader.fieldnames or []
        return []

    def get_data_url(self) -> str:
        return reverse("chart-data-csv", args=[self.uuid])

    general_panels = [
        FieldPanel("name"),
        MultiFieldPanel(
            heading="Descriptive text",
            children=[
                FieldPanel("title"),
                FieldPanel("subtitle"),
                FieldPanel("caption"),
            ],
        ),
        MultiFieldPanel(
            heading="Style",
            children=[
                FieldPanel("theme"),
                FieldPanel("height"),
                FieldPanel("show_value_labels"),
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

    data_panels = [
        FieldPanel("data_source"),
        FieldPanel("data_file"),
        FieldPanel("data_manual"),
    ]

    axis_panels = [
        MultiFieldPanel(
            heading=_("X axis"),
            children=[
                FieldPanel("x_type"),
                FieldPanel("x_label"),
                FieldRowPanel(
                    [
                        FieldPanel("x_min"),
                        FieldPanel("x_max"),
                    ]
                ),
                FieldPanel("x_reversed"),
                FieldPanel("x_tick_interval"),
            ],
        ),
        MultiFieldPanel(
            heading=_("Y axis"),
            children=[
                FieldPanel("y_type"),
                FieldPanel("y_label"),
                FieldPanel("y_value_suffix"),
                FieldPanel("y_tooltip_suffix"),
                FieldRowPanel(
                    [
                        FieldPanel("y_min"),
                        FieldPanel("y_max"),
                    ]
                ),
                FieldPanel("y_reversed"),
                FieldPanel("y_tick_interval"),
            ],
        ),
    ]

    @property
    def highcharts_chart_type(self):
        raise NotImplementedError

    @classproperty
    def edit_handler(cls):  # pylint: disable=no-self-argument
        return TabbedInterface(
            [
                ObjectList(cls.general_panels, heading=_("General")),
                ObjectList(cls.data_panels, heading=_("Data")),
                ObjectList(cls.axis_panels, heading=_("Axes")),
            ]
        )

    def get_highcharts_config(self, row_data: list[dict[str, list]] | None) -> dict[str, Any]:
        config = {
            "chart": {
                "type": self.highcharts_chart_type,
                "height": self.height,
            },
            "colors": HIGHCHARTS_THEMES[self.theme],
            "title": {
                "text": self.title or self.name,
            },
            "legend": {
                "align": "left",
                "enabled": self.show_legend,
                "verticalAlign": self.legend_position,
            },
            "xAxis": self.get_x_axis_config(row_data),
            "yAxis": self.get_y_axis_config(row_data),
            "plotOptions": self.get_plot_options(),
            "navigation": {
                "enabled": False,
            },
            "credits": {
                "enabled": False,
            },
        }
        if self.subtitle:
            config["subtitle"] = {
                "text": self.subtitle,
            }
        if self.caption:
            config["caption"] = {
                "text": expand_db_html(self.caption),
                "useHTML": True,
            }
        if row_data is not None:
            config["series"] = self.get_series_data(row_data)
        else:
            config["data"] = {"csvURL": self.get_data_url()}
        return config

    def get_x_axis_config(self, row_data: list[dict[str, list]] | None = None) -> dict[str, Any]:
        def format_category(value):
            try:
                return float(value) if self.x_type in (AxisValueType.NUMBER, AxisValueType.DATETIME) else value
            except ValueError:
                return value

        config = {
            "type": "linear" if row_data else "category",
            "title": {
                "enabled": True,
                "text": self.x_label or self.headers[0],
            },
            "lineColor": "#929292",
            "lineWidth": 1,
            "reversed": self.x_reversed,
        }
        if self.x_tick_interval is not None:
            config["tickInterval"] = self.x_tick_interval
        if row_data is not None:
            config["categories"] = [format_category(r[0]) for r in row_data]
        if self.x_min is not None:
            config["min"] = self.x_min
        if self.x_max is not None:
            config["max"] = self.x_max
        return config

    def get_y_axis_config(
        self,
        row_data: list[dict[str, list]] | None = None,  # pylint: disable=unused-argument
    ) -> dict[str, Any]:
        config = {
            "reversed": self.y_reversed,
            "lineColor": "#929292",
            "lineWidth": 1,
            "endOnTick": False,
        }
        label = self.y_label or self.headers[1]
        if label:
            config["title"] = (
                {
                    "enabled": True,
                    "text": label,
                },
            )
        if self.y_tick_interval is not None:
            config["tickInterval"] = self.y_tick_interval
        if self.y_value_suffix:
            config["labels"] = {
                "format": "{value} " + self.y_value_suffix,
            }
        if self.y_min is not None:
            config["min"] = self.y_min
        if self.y_max is not None:
            config["max"] = self.y_max
        return config

    def get_plot_options(self) -> dict[str, Any]:
        return {
            "series": {
                "borderWidth": 0,
                "animation": False,
                "pointPadding": 0.1,
                "groupPadding": 0.1,
                "dataLabels": {
                    "enabled": self.show_value_labels,
                },
            }
        }

    def get_series_data(self, rows: list[dict[str, list]]) -> list[dict[str, Any]]:
        def format_value(value):
            try:
                return float(value) if self.y_type in (AxisValueType.NUMBER, AxisValueType.DATETIME) else value
            except ValueError:
                return value

        series = []
        for i, column in enumerate(self.headers[1:], start=1):
            item = {
                "name": column,
                "data": [format_value(row[i]) for row in rows],
            }
            if self.y_tooltip_suffix:
                item["tooltip"] = {
                    "valueSuffix": self.y_tooltip_suffix,
                }
            series.append(item)
        return series


class LineChart(BaseHighchartsChart):
    highcharts_chart_type = "line"
    template = "templates/components/charts/line_chart.html"

    class Meta:
        verbose_name = _("line chart")
        verbose_name_plural = _("line charts")


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

    @property
    def highcharts_chart_type(self):
        return self.subtype.split("_")[-1]

    def get_plot_options(self) -> dict[str, Any]:
        config = super().get_plot_options()
        if self.is_stacked():
            config[self.highcharts_chart_type] = {"stacking": "normal"}
        return config

    general_panels = [FieldPanel("subtype")] + BaseHighchartsChart.general_panels
