import uuid

from django import forms
from django.core.files import File
from django.db.models import FileField
from django.utils.translation import gettext_lazy as _
from wagtail.admin.forms.models import WagtailAdminDraftStateFormMixin

from ons_alpha.charts.models import Chart
from ons_alpha.charts.utils import get_chart_type_choices


class ChartCopyForm(WagtailAdminDraftStateFormMixin):

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

        # Create copies of files
        for field in self.instance._meta.get_fields():
            if isinstance(field, FileField) and (original_file := getattr(self.instance, field.attname, None)):
                storage = field.storage
                # Copy the file using the storage backend
                with original_file.open("rb") as source_file:
                    new_name = storage.save(original_file.name, source_file)
                new_file = File(storage.open(new_name), name=new_name)
                setattr(self.instance, field.attname, new_file)
        return super().save(commit)


class ChartTypeSelectForm(forms.Form):
    chart_type = forms.ChoiceField(
        choices=get_chart_type_choices, label=_("What type of chart do you want to create?"), required=True
    )
