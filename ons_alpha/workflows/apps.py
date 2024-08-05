from django.apps import AppConfig


class WorkflowsAppConfig(AppConfig):
    name = "ons_alpha.workflows"

    def ready(self):
        # note: using a monkey patch until https://github.com/wagtail/wagtail/pull/6025 is fixed
        # Currently scheduled for 6.3 in November
        import ons_alpha.workflows.monkey_patches  # noqa pylint: disable=unused-import,import-outside-toplevel
