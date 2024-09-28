from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from wagtail.admin.forms import WagtailAdminModelForm

from ons_alpha.charts.constants import DataSource
from ons_alpha.charts.utils import get_chart_type_choices


class ChartTypeSelectForm(forms.Form):
    chart_type = forms.ChoiceField(
        choices=get_chart_type_choices, required=True
    )

class BaseChartEditForm(WagtailAdminModelForm):
    data_source = forms.ChoiceField(label=_("Data source"), choices=DataSource.choices, initial=DataSource.CSV)

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data["data_source"] == DataSource.CSV and not cleaned_data["data_file"]:
            raise ValidationError({"data_file": _("This field is required")})
        if cleaned_data["data_source"] == DataSource.MANUAL and not cleaned_data["data"]:
            raise ValidationError({"data_file": _("This field is required")})
        return cleaned_data
