from django import forms
from wagtail.admin.forms import WagtailAdminPageForm
from .models import BulletinPage

class BulletinPageAdminForm(WagtailAdminPageForm):
    previous_version = forms.CharField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = BulletinPage
        fields = '__all__'

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
