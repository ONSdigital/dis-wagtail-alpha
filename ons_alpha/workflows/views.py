import json

from django.shortcuts import redirect
from wagtail.admin.views.pages.edit import EditView as WagtailPageEditView
from wagtail.models import COMMENTS_RELATION_NAME, Page

from ons_alpha.workflows.models import ReadOnlyGroupTask


class EditView(WagtailPageEditView):
    def post(self, request):
        if isinstance(self.page.current_workflow_task, ReadOnlyGroupTask) and not self.request.user.is_superuser:
            # temporarily mark as non-locked
            self.locked_for_user = False  # pylint: disable=attribute-defined-outside-init

        return super().post(request)

    def perform_workflow_action(self):
        """
        Note: this skips saving a draft when the workflow task is a ReadyOnlyGroupTask
        """
        if self.request.user.is_superuser:
            return super().perform_workflow_action()

        self.page: Page = self.form.save(commit=not self.page.live)  # pylint: disable=attribute-defined-outside-init
        if not isinstance(self.page.current_workflow_task, ReadOnlyGroupTask):
            return super().perform_workflow_action()

        self.subscription.save()

        if self.has_content_changes and "comments" in self.form.formsets:
            for comment in getattr(self.page, COMMENTS_RELATION_NAME).filter(pk__isnull=True):
                # We need to ensure comments have an id in the revision, so positions can be identified correctly
                comment.save()

            changes = self.get_commenting_changes()
            self.log_commenting_changes(changes, self.page.get_latest_revision())
            self.send_commenting_notifications(changes)

        extra_workflow_data_json = self.request.POST.get("workflow-action-extra-data", "{}")
        extra_workflow_data = json.loads(extra_workflow_data_json)
        self.page.current_workflow_task.on_action(
            self.page.current_workflow_task_state,
            self.request.user,
            self.workflow_action,
            **extra_workflow_data,
        )

        self.add_save_confirmation_message()

        response = self.run_hook("after_edit_page", self.request, self.page)
        if response:
            return response

        # we're done here - redirect back to the explorer
        return redirect("wagtailadmin_explore", self.page.get_parent().id)
