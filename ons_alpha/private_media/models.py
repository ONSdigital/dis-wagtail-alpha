import logging

from collections import defaultdict
from collections.abc import Iterable

from django.conf import settings
from django.core.files.base import File
from django.db import models
from django.db.models.fields.files import FieldFile
from django.utils import timezone
from wagtail.documents.models import DocumentQuerySet
from wagtail.images.models import AbstractRendition, Filter, ImageQuerySet
from wagtail.models import Collection, CollectionMember

from ons_alpha.private_media import utils
from ons_alpha.private_media.constants import PRIVATE_FILE_ACL, PUBLIC_FILE_ACL


logger = logging.getLogger(__name__)


class ProtectedCollection(models.Model):
    """
    A model that exists entirely to prevent accidental deletion of the
    special 'Private' and 'Public' collections used by this app to determine
    the privacy of media. The only objects that should be created are for the
    'Private' and 'Public' collections - which happens in a data migration.
    """

    collection = models.OneToOneField(Collection, on_delete=models.PROTECT)

    def __str__(self):
        return f"Exists to prevent accidental deletion of {self.collection!r}"


class PrivateMediaManager(models.Manager):
    """
    A custom model `Manager` to be used by concrete subclasses of
    `PrivateMediaCollectionMember`. It includes several methods for
    applying privacy-related changes to multiple objects at the same
    time.
    """

    managed_privacy_fields = (
        "is_private",
        "last_public_collection",
        "last_private_collection",
        "privacy_last_changed",
        "acls_last_set",
    )

    def bulk_make_public(self, objects: list["PrivateMediaCollectionMember"]) -> int:
        """
        Make a list of objects of this type 'public' as efficiently as
        possible. Returns the number of objects that were actually updated
        in response to the request.
        """
        to_update = []
        for obj in objects:
            if obj.move_to_public_collection():
                obj.determine_privacy()
                to_update.append(obj)
        if not to_update:
            return 0

        count = self.bulk_update(to_update, fields=self.managed_privacy_fields)
        self.bulk_set_file_acls(to_update, PUBLIC_FILE_ACL)
        return count

    def bulk_make_private(self, objects: list["PrivateMediaCollectionMember"]) -> int:
        """
        Make a list of objects of this type 'private' as efficiently as
        possible. Returns the number of objects that were actually updated
        in response to the request.
        """
        to_update = []
        for obj in objects:
            if obj.move_to_private_collection():
                obj.determine_privacy()
                to_update.append(obj)
        if not to_update:
            return 0

        count = self.bulk_update(to_update, fields=self.managed_privacy_fields)
        self.bulk_set_file_acls(to_update, PRIVATE_FILE_ACL)
        return count

    def bulk_set_file_acls(self, objects: list["PrivateMediaCollectionMember"], acl_name: str) -> int:
        """
        For a list of objects of this type, set the ACLs for all related
        files to either 'public' or 'private'. Returns the number of objects
        for which all related files were successfully updated - which will
        also have their 'acls_last_set' datetime updated.
        """
        successfully_updated_objects = []
        files_by_object: dict[PrivateMediaCollectionMember, list[FieldFile]] = defaultdict(list)
        all_files = []

        for obj in objects:
            for file in obj.get_privacy_controlled_files():
                all_files.append(file)
                files_by_object[obj].append(file)

        results = utils.set_file_acls(all_files, acl_name)

        for obj, files in files_by_object:
            if all(results.get(file) for file in files):
                obj.acls_last_set = timezone.now()
                successfully_updated_objects.append(obj)

        if successfully_updated_objects:
            return self.bulk_update(successfully_updated_objects, fields=["acls_last_set"])

        return 0


class PrivateMediaCollectionMember(CollectionMember):
    """
    An abstract model class that can either be used a mixin to apply
    privacy-related functionality to existing `CollectionMember`
    models, or as a base model for new ones.

    It contains fields for tracking:
    - Whether the collection an object currently belongs to is private or public
    - The last 'public' collection the object belonged to
    - The last 'private' collection the object belonged to
    - A timestamp to indicate when the object's privacy was last changed as the
      result of a change to it's collection value
    - A timestamp to indicate when the ACLs were last successfully set for the
      object's associated files

    Where individual objects are updated (usually via the Wagtail UI), changes to
    managed field values are written to the database by the overridden
    `save()` method.

    Where multiple objects are updated at once (e.g. via a signal handler or
    management command running the server), changes to managed field values
    are written to the database by the bulk update methods provided by
    `PrivateMediaManager`.
    """

    is_private = models.BooleanField(default=False, editable=False)
    last_public_collection = models.ForeignKey(
        Collection,
        null=True,
        editable=False,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    last_private_collection = models.ForeignKey(
        Collection,
        null=True,
        editable=False,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    privacy_last_changed = models.DateTimeField(null=True, editable=False)
    acls_last_set = models.DateTimeField(null=True, editable=False)

    objects = PrivateMediaManager()

    class Meta:
        abstract = True

    def save(self, *args, set_file_acls: bool = True, **kwargs) -> None:
        # Set managed field values
        self.determine_privacy()
        # Save model field changes at this point
        super().save(*args, **kwargs)

        # Trigger ACL updates after-the-fact
        if set_file_acls and (
            self.acls_last_set is None or (self.privacy_last_changed and self.acls_last_set < self.privacy_last_changed)
        ):
            acl_name = PRIVATE_FILE_ACL if self.is_private else PUBLIC_FILE_ACL
            results = utils.set_file_acls(self.get_privacy_controlled_files(), acl_name)
            # Only update 'acls_last_set' if all ACL updates were successfull
            if set(results.values()) == {True}:
                self.acls_last_set = timezone.now()
                kwargs["update_fields"] = ["acls_last_set"]
                super().save(*args, **kwargs)

    @property
    def is_public(self) -> bool:
        return not self.is_private

    def determine_privacy(self) -> bool:
        was_private = self.is_private
        privacy_changed = False
        self.is_private = self.collection.path.startswith(utils.get_private_root_collection_path())
        if self.is_private:
            self.last_private_collection = self.collection
            privacy_changed = not was_private
        else:
            self.last_public_collection = self.collection
            privacy_changed = was_private
        if not self.pk or privacy_changed:
            self.privacy_last_changed = timezone.now()
        return privacy_changed

    def move_to_private_collection(self) -> bool:
        """
        Set this object's collection to one that is 'Private', without saving any
        changes. Returns a bool indicating whether there was any change (e.g. if
        the object already belongs to a private collection, `False` is returned).
        """
        if self.collection.path.startswith(utils.get_private_root_collection_path()):
            return False
        # Use 'last_private_collection' - but only if it is still private
        if self.last_private_collection and self.last_private_collection.path.startswith(
            utils.get_private_root_collection_path()
        ):
            self.collection = self.last_private_collection
        else:
            # Fallback to the root private collection
            self.collection_id = (  # pylint: disable=attribute-defined-outside-init
                utils.get_private_root_collection_id()
            )
        return True

    def move_to_public_collection(self) -> bool:
        """
        Set this object's collection to one that is 'Public', without saving any
        changes. Returns a bool indicating whether there was any change (e.g. if
        the object already belongs to a public collection, `False` is returned).
        """
        if self.collection.path.startswith(utils.get_public_root_collection_path()):
            return False
        # Use 'last_public_collection' - but only if it is still public
        if self.last_public_collection and self.last_public_collection.path.startswith(
            utils.get_public_root_collection_path()
        ):
            self.collection = self.last_public_collection
        else:
            # Fallback to the root public collection
            self.collection_id = utils.get_public_root_collection_id()  # pylint: disable=attribute-defined-outside-init
        return True

    def get_privacy_controlled_files(self) -> Iterable[FieldFile]:
        raise NotImplementedError


class PrivateImageManager(PrivateMediaManager):
    """
    A subclass of `PrivateMediaManager` that returns instances of
    Wagtail's custom `ImageQuerySet`, which includes image-specific
    filter methods other functionality that Wagtail itself depends on.
    """

    def get_queryset(self):
        return ImageQuerySet(self.model, using=self._db)


class PrivateImageMixin(PrivateMediaCollectionMember):
    """
    A mixin class to be applied to a project's custom Image model,
    allowing the privacy to be controlled effectively, depending on the
    collection the image belongs to.
    """

    objects = PrivateImageManager()

    class Meta:
        abstract = True

    def get_privacy_controlled_files(self) -> Iterable[File]:
        if self.file:
            yield self.file
        for rendition in self.renditions.all():
            yield rendition.file

    def create_renditions(self, *filters: Filter) -> dict[Filter, AbstractRendition]:
        created_renditions = super().create_renditions(*filters)
        new_rendition_acl = None
        if self.is_private and getattr(settings, "AWS_DEFAULT_ACL", PRIVATE_FILE_ACL) != PRIVATE_FILE_ACL:
            new_rendition_acl = PRIVATE_FILE_ACL
        elif self.is_public and getattr(settings, "AWS_DEFAULT_ACL", PUBLIC_FILE_ACL) != PUBLIC_FILE_ACL:
            new_rendition_acl = PUBLIC_FILE_ACL
        if new_rendition_acl:
            utils.set_file_acls([r.file for r in created_renditions.values()], new_rendition_acl)
        return created_renditions


class PrivateAbstractRendition(AbstractRendition):
    """
    A replacement for Wagtail's built-in `AbstractRendition` model, that should be used as
    a base for rendition models for image models subclassing `PrivateImageMixin`. This
    is necessary to ensure that only users with relevant permissions can view renditions
    for private images.
    """

    class Meta:
        abstract = True

    @staticmethod
    def construct_cache_key(image, filter_cache_key, filter_spec):
        """
        Overrides AbstractRendition.construct_cache_key() to include an
        indication of whether the image is private or not.
        """
        return "wagtail-rendition-" + "-".join(
            [str(image.id), image.file_hash, str(image.is_private), filter_cache_key, filter_spec]
        )

    @property
    def url(self):
        """
        For private images, or images that haven't yet had their ACLs set
        succesfully, redirect users to a view that is capable of checking
        permissions and serving the file.

        For public images that have undergone succesful ACL-setting attempts,
        return the file URL, so that S3 (or other active media backend)
        handles the request.
        """
        from wagtail.images.views.serve import generate_image_url  # pylint: disable=import-outside-toplevel

        if self.image.is_public and self.image.acls_last_set > self.image.privacy_last_changed:
            return self.file.url
        return generate_image_url(self.image, self.filter_spec)


class PrivateDocumentManager(PrivateMediaManager):
    """
    A subclass of `PrivateMediaManager` that returns instances of
    Wagtail's custom `DocumentQuerySet`, which includes document-specific
    filter methods other functionality that Wagtail itself depends on.
    """

    def get_queryset(self):
        return DocumentQuerySet(self.model, using=self._db)


class PrivateDocumentMixin(PrivateMediaCollectionMember):
    """
    A mixin class to be applied to a project's custom Document model,
    allowing the privacy to be controlled effectively, depending on the
    collection the image belongs to.
    """

    objects = PrivateDocumentManager()

    class Meta:
        abstract = True

    def get_privacy_controlled_files(self) -> Iterable[FieldFile]:
        if self.file:
            yield self.file
