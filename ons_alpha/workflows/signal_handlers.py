from wagtail.models import TaskState
from wagtail.signals import task_submitted

from ons_alpha.workflows.models import TaskStateSubmissionEmailNotifier


task_submission_email_notifier = TaskStateSubmissionEmailNotifier()


def register_signal_handlers():
    task_submitted.connect(
        task_submission_email_notifier,
        sender=TaskState,
        dispatch_uid="ons_group_approval_task_submitted_email_notification",
    )
