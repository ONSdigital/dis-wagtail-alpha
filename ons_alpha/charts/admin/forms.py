import uuid

from django import forms
from django.utils.translation import gettext_lazy as _
from wagtail.admin.forms.models import WagtailAdminDraftStateFormMixin

from ons_alpha.charts.models import Chart
from ons_alpha.charts.utils import get_chart_type_choices


class ChartCopyForm(WagtailAdminDraftStateFormMixin, forms.ModelForm):

    class Meta:
        model = Chart
        fields = ["name"]
        labels = {
            "name": _("New chart name"),
        }

    def save(self, commit=True):
        # Override values to create a new draft object
        self.instance.id = None
        self.instance.pk = None
        self.instance.uuid = uuid.uuid4()
        self.instance.live = False
        self.instance._state.adding = True
        # Bypass validation for missing 'data_file' values
        self.instance.is_copy = True
        self.instance.data_file = None
        return super().save(commit)


class ChartTypeSelectForm(forms.Form):
    chart_type = forms.ChoiceField(
        choices=get_chart_type_choices, label=_("What type of chart do you want to create?"), required=True
    )
