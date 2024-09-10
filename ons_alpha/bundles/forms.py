from typing import TYPE_CHECKING

from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from wagtail.admin.forms import WagtailAdminModelForm

from ons_alpha.bundles.enums import ACTIVE_BUNDLE_STATUS_CHOICES, BundleStatus

from ..workflows.models import ReadyToPublishGroupTask


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

    def _validate_bundled_pages(self):
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

    def _validate_bundled_pages_status(self):
        page_state_errors = []
        for form in self.formsets["bundled_pages"].forms:
            if form.cleaned_data["DELETE"]:
                continue

            if page := form.clean().get("page"):
                page = page.specific

                workflow_state = page.current_workflow_state
                if not (
                    workflow_state
                    and isinstance(workflow_state.current_task_state.task.specific, ReadyToPublishGroupTask)
                ):
                    page_state_errors.append(f"{page.get_admin_display_title()} is not ready to be published")

        if page_state_errors:
            self.cleaned_data["status"] = self.instance.status
            raise ValidationError(page_state_errors)

    def clean(self):
        cleaned_data = super().clean()

        self._validate_bundled_pages()

        status = cleaned_data["status"]
        if self.instance.status != status:
            # the status has changed, let's check
            if status == BundleStatus.APPROVED:
                if self.instance.created_by_id == self.for_user.pk:
                    cleaned_data["status"] = self.instance.status
                    self.add_error("status", ValidationError("You cannot self-approve your own bundle!"))

                self._validate_bundled_pages_status()

                cleaned_data["approved_at"] = timezone.now()
                cleaned_data["approved_by"] = self.for_user
            elif self.instance.status == BundleStatus.APPROVED:
                cleaned_data["approved_at"] = None
                cleaned_data["approved_by"] = None

        return cleaned_data
