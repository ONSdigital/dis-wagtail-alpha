from django.core.exceptions import ValidationError

from ons_alpha.private_media import utils


class PrivacyAwareCollectionFormMixin:
    """
    Used by `private_media.wagtail_patches.patch_collection_edit_form()` to add additional
    validation to the 'parent' field in `wagtail.admin.forms.collections.CollectionForm`,
    preventing a currently 'Private' collection from being moved to a 'Public' one, and
    vica-versa.
    """

    def clean_parent(self):
        parent = self.cleaned_data["parent"]
        if self.instance and self.instance.pk:
            if utils.collection_is_private(self.instance) and utils.collection_is_public(parent):
                raise ValidationError(
                    "A collection cannot be moved from the 'Private' branch to the 'Public' branch. "
                    "Please create a new collection and manually reassign the contents."
                )
            if utils.collection_is_public(self.instance) and utils.collection_is_private(parent):
                raise ValidationError(
                    "A collection cannot be moved from the 'Public' branch to the 'Private' branch. "
                    "Please create a new collection and manually reassign the contents."
                )
        super().clean_parent()
