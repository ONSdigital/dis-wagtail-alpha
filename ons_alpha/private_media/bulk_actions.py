from django.utils import timezone

from ons_alpha.private_media import utils
from ons_alpha.private_media.constants import PRIVATE_FILE_ACL, PUBLIC_FILE_ACL


class BulkCollectionUpdateMixin:
    """
    Used by `private_media.wagtail_patches.patch_bulk_action_views()` to patch
    Wagtail's built-in `AddToCollectionBulkAction` bulk action views, so that if
    images or documents are moved from a 'Private' collection to a 'Public' one
    (or vica-versa), the automatically-managed privacy-related field values are
    updated accordingly, and the ACL is correctly updated for any associated
    files in S3.
    """

    @classmethod
    def apply_collection_update_to_objects(cls, object_list, collection):
        if collection is None:
            return None

        original_collections = {obj: obj.collection for obj in object_list}

        update_kwargs = {"collection": collection}

        if utils.collection_is_private(collection):
            update_kwargs.update(last_private_collection=collection)
        else:
            update_kwargs.update(last_public_collection=collection)

        num_parent_objects = (
            cls.get_default_model().objects.filter(pk__in=[obj.pk for obj in object_list]).update(**update_kwargs)
        )

        now = timezone.now()
        if utils.collection_is_private(collection):
            newly_private_objects = []
            for obj, original_collection in original_collections.items():
                if utils.collection_is_public(original_collection):
                    obj.privacy_last_changed = now
                    newly_private_objects.append(obj)
            if newly_private_objects:
                cls.get_default_model().objects.bulk_update(newly_private_objects, fields=["privacy_last_changed"])
                cls.get_default_model().objects.bulk_set_file_acls(newly_private_objects, PRIVATE_FILE_ACL)
        else:
            newly_public_objects = []
            for image, original_collection in original_collections.items():
                if utils.collection_is_private(original_collection):
                    image.privacy_last_changed = now
                    newly_public_objects.append(image)
            if newly_public_objects:
                cls.get_default_model().objects.bulk_update(newly_public_objects, fields=["privacy_last_changed"])

                cls.get_default_model().objects.bulk_set_file_acls(newly_public_objects, PUBLIC_FILE_ACL)

        return num_parent_objects, 0
