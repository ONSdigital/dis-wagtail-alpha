from django.apps import AppConfig


class InlineindexConfig(AppConfig):
    default_auto_field = "django.db.models.AutoField"
    name = "ons_alpha.inlineindex"

    def ready(self):
        from . import signal_handlers  # noqa
