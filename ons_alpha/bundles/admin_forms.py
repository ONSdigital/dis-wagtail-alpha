from django import forms
from django.utils.translation import gettext as _

from .models import Bundle
from .viewsets import BundleChooserWidget


class AddToBundleForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.page_to_add = kwargs.pop("page_to_add")

        super().__init__(*args, **kwargs)

        self.fields["bundle"] = forms.ModelChoiceField(
            queryset=Bundle.objects.editable(),
            widget=BundleChooserWidget(),
            label=_("Bundle"),
            help_text=_("Select a bundle for this page."),
        )
