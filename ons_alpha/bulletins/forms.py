from django import forms
from django.apps import apps
from wagtail.admin.forms import WagtailAdminPageForm


class BulletinPageAdminForm(WagtailAdminPageForm):
    previous_version = forms.CharField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = apps.get_model("bulletins", "BulletinPage")  # Lazy reference to avoid circular dependency
        fields = "__all__"

    def clean(self):
        cleaned_data = super().clean()

        # Remove duplicate topics
        chosen = []
        for idx, form in enumerate(self.formsets["topics"].forms):
            if not form.is_valid():
                continue
            topic = form.clean().get("topic")
            if topic in chosen:
                self.formsets["topics"].forms[idx].cleaned_data["DELETE"] = True
            else:
                chosen.append(topic)

        return cleaned_data
