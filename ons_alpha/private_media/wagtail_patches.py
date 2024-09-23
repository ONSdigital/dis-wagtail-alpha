from ons_alpha.private_media.bulk_actions import BulkCollectionUpdateMixin
from ons_alpha.private_media.forms import PrivacyAwareCollectionFormMixin


def patch_bulk_action_views():
    """
    Patches Wagtail's built-in `AddToCollectionBulkAction` views for images
    and documents, so that they use `private_media.bulk_actions.BulkCollectionUpdateMixin`
    to apply necessary additional changes.
    """

    from wagtail.documents.views import bulk_actions as document_bulk_actions  # pylint: disable=import-outside-toplevel
    from wagtail.images.views import bulk_actions as image_bulk_actions  # pylint: disable=import-outside-toplevel

    class AddDocumentsToCollectionBulkAction(
        BulkCollectionUpdateMixin, document_bulk_actions.AddToCollectionBulkAction
    ):

        @classmethod
        def execute_action(cls, objects, collection=None, **kwargs):
            return cls.apply_collection_update_to_objects(objects, collection)

    class AddImagesToCollectionBulkAction(BulkCollectionUpdateMixin, image_bulk_actions.AddToCollectionBulkAction):

        @classmethod
        def execute_action(cls, images, collection=None, **kwargs):
            return cls.apply_collection_update_to_objects(images, collection)

    image_bulk_actions.AddToCollectionBulkAction = AddImagesToCollectionBulkAction
    document_bulk_actions.AddToCollectionBulkAction = AddDocumentsToCollectionBulkAction


def patch_collection_edit_form():
    """
    Patches Wagtail's built-in `CollectionForm` to include the custom validation
    logic from `PrivacyAwareCollectionFormMixin` (above).
    """

    from wagtail.admin.forms import collections  # pylint: disable=import-outside-toplevel

    class PrivacyAwareCollectionForm(PrivacyAwareCollectionFormMixin, collections.CollectionForm):
        pass

    collections.CollectionForm = PrivacyAwareCollectionForm
