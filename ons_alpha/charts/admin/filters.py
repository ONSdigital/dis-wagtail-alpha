from django.forms import CheckboxSelectMultiple
from django.utils.translation import gettext_lazy as _
from django_filters.filters import DateFromToRangeFilter
from wagtail.admin.filters import (
    DateRangePickerWidget,
    MultipleContentTypeFilter,
    WagtailFilterSet,
)

from ons_alpha.charts.models import Chart
from ons_alpha.charts.utils import get_chart_content_types


class ChartFilterSet(WagtailFilterSet):
    latest_revision_created_at = DateFromToRangeFilter(
        label=_("Date updated"),
        widget=DateRangePickerWidget,
    )
    content_type = MultipleContentTypeFilter(
        label=_("Chart type"),
        queryset=lambda request: get_chart_content_types(),
        widget=CheckboxSelectMultiple,
    )
    first_published_at = DateFromToRangeFilter(
        label=_("First published"),
        widget=DateRangePickerWidget,
    )
    last_published_at = DateFromToRangeFilter(
        label=_("Last published"),
        widget=DateRangePickerWidget,
    )

    class Meta:
        model = Chart
        fields = [
            "content_type",
            "is_template",
            "live",
            "latest_revision_created_at",
            "first_published_at",
            "last_published_at",
        ]
