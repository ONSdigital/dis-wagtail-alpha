from wagtail.admin.forms import WagtailAdminPageForm

class BulletinPageAdminForm(WagtailAdminPageForm):
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
