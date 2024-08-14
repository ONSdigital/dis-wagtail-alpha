from django.utils.translation import gettext_lazy as _
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
