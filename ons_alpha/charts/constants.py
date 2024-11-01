from django.db.models import TextChoices
from django.utils.translation import gettext_lazy as _


class AxisValueType(TextChoices):
    TEXT = "category", _("Text")
    NUMBER = "linear", _("Number")
    DATETIME = "datetime", _("Datetime")


class AnnotationStyle(TextChoices):
    ABOVE_LINE = "above_line", _("Above line")
    BELOW_LINE = "below_line", _("Below line")


class DataSource(TextChoices):
    CSV = "csv", _("Upload a CSV")
    MANUAL = "manual", _("Input data manually")


class BarChartType(TextChoices):
    BAR = "bar", _("Bar")
    STACKED_BAR = "stacked_bar", _("Stacked bar")
    COLUMN = "column", _("Column")
    STACKED_COLUMN = "stacked_column", _("Stacked column")


class HighchartsTheme(TextChoices):
    PRIMARY = "primary", _("Primary")
    ALTERNATE = "alternate", _("Alternate")


class LegendPosition(TextChoices):
    TOP = "top", _("Top")
    BOTTOM = "bottom", _("Bottom")
