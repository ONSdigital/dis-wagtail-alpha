from django.utils.translation import gettext_lazy as _
from wagtail.admin.mail import GroupApprovalTaskStateSubmissionEmailNotifier
from wagtail.models import AbstractGroupApprovalTask


class ReadOnlyGroupTask(AbstractGroupApprovalTask):
    def user_can_access_editor(self, obj, user):
        return True

    def locked_for_user(self, obj, user):
        return not user.is_superuser

    @classmethod
    def get_description(cls):
        return _("Members of the chosen Wagtail Groups can approve this task, but they cannot change any content")

    class Meta:
        verbose_name = _("Read-only Group approval task")
        verbose_name_plural = _("Read-only Group approval tasks")


class ReadyToPublishGroupTask(AbstractGroupApprovalTask):
    """
    Placeholder task model to use in the Bundle approval logic
    """

    @classmethod
    def get_description(cls):
        return _("Denotes a page that is ready to be published. Use by bundles.")

    class Meta:
        verbose_name = _("Ready to publish Group approval task")
        verbose_name_plural = _("Ready to publish Group approval tasks")


class TaskStateSubmissionEmailNotifier(GroupApprovalTaskStateSubmissionEmailNotifier):
    """A notifier to send email updates for our submission events"""

    def can_handle(self, instance, **kwargs):
        return isinstance(instance, self.valid_classes) and isinstance(
            instance.task.specific, (ReadOnlyGroupTask, ReadyToPublishGroupTask)
        )
