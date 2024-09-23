from django.apps import AppConfig


class PrivateMediaConfig(AppConfig):
    default_auto_field = "django.db.models.AutoField"
    name = "ons_alpha.private_media"

    def ready(self) -> None:
        from .signal_handlers import register_signal_handlers  # pylint: disable=import-outside-toplevel
        from .wagtail_patches import (  # pylint: disable=import-outside-toplevel
            patch_bulk_action_views,
            patch_collection_edit_form,
        )

        patch_bulk_action_views()
        patch_collection_edit_form()
        register_signal_handlers()
