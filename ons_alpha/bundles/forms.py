from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _
from wagtail.admin.forms import WagtailAdminModelForm


class BundleAdminForm(WagtailAdminModelForm):
    def clean(self):
        cleaned_data = super().clean()

        for idx, form in enumerate(self.formsets["bundled_pages"].forms):
            if not form.is_valid():
                continue

            page = form.clean().get("page")
            if page is None:
                # tidy up in case the page reference is empty
                self.formsets["bundled_pages"].forms[idx].cleaned_data["DELETE"] = True
            else:
                page = page.specific
                if page.in_active_bundle and page.active_bundle != self.instance and not form.cleaned_data["DELETE"]:
                    raise ValidationError(f"{page} is already in an active bundle ({page.active_bundle})")

        return cleaned_data


class AddToBundleForm(forms.Form):
    def __init__(self, *args, **kwargs):
        # imported inline to avoid circular imports
        from .models import Bundle
        from .viewsets import BundleChooserWidget

        self.page_to_add = kwargs.pop("page_to_add")

        super().__init__(*args, **kwargs)

        self.fields["bundle"] = forms.ModelChoiceField(
            queryset=Bundle.active_objects.all(),
            widget=BundleChooserWidget(),
            label=_("Bundle"),
            help_text=_("Select a bundle for this page."),
        )
