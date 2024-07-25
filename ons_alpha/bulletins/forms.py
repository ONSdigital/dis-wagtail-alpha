from django.forms import ValidationError
from wagtail.admin.forms import WagtailAdminPageForm
from wagtail.models import PageLogEntry


class BulletinPageAdminForm(WagtailAdminPageForm):
    def clean_updates(self):
        updates = self.cleaned_data["updates"]

        latest_published_revision_id = (
            PageLogEntry.objects.filter(page=self.instance, action="wagtail.publish")
            .order_by("-timestamp")
            .values_list("revision_id", flat=True)
            .first()
        )
        page_revision_ids = set(self.instance.revisions.order_by().values_list("id", flat=True).distinct())

        for update in updates:
            if update.block_type != "correction":
                continue

            if update.value["previous_version"] and int(update.value["previous_version"]) not in page_revision_ids:
                # Prevent tampering
                self.add_error("updates", ValidationError("The chosen revision is not valid for the current page"))
            elif latest_published_revision_id is not None:
                # If there's no value, set it to the latest revision
                update.value["previous_version"] = latest_published_revision_id

        return updates

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
