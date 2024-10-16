from django import forms
from django.utils.translation import gettext_lazy as _

from ons_alpha.charts.utils import get_chart_type_choices


class ChartTypeSelectForm(forms.Form):
    chart_type = forms.ChoiceField(
        choices=get_chart_type_choices, label=_("What type of chart do you want to create?"), required=True
    )
