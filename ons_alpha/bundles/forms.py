from typing import TYPE_CHECKING

from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from wagtail.admin.forms import WagtailAdminModelForm

from ons_alpha.bundles.enums import ACTIVE_BUNDLE_STATUS_CHOICES, BundleStatus


if TYPE_CHECKING:
    from .models import Bundle


class BundleAdminForm(WagtailAdminModelForm):
    instance: "Bundle" = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # hides the "Released" status choice
        self.fields["status"].choices = ACTIVE_BUNDLE_STATUS_CHOICES

        # fully hide and disable the approved_at/by fields to prevent form tampering
        self.fields["approved_at"].disabled = True
        self.fields["approved_at"].widget = forms.HiddenInput()
        self.fields["approved_by"].disabled = True
        self.fields["approved_by"].widget = forms.HiddenInput()

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

        status = cleaned_data["status"]
        if self.instance.status != status:
            # the status has changed, let's check
            if status == BundleStatus.APPROVED:
                if self.instance.created_by_id == self.for_user.pk:
                    raise ValidationError("You cannot self-approve your own bundle!")

                cleaned_data["approved_at"] = timezone.now()
                cleaned_data["approved_by"] = self.for_user
            elif self.instance.status == BundleStatus.APPROVED:
                cleaned_data["approved_at"] = None
                cleaned_data["approved_by"] = None

        return cleaned_data
