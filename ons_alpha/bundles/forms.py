from django.core.exceptions import ValidationError
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
