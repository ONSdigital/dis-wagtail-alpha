import concurrent.futures
import logging

from collections.abc import Iterable
from functools import lru_cache
from typing import NamedTuple

from botocore.exceptions import ClientError
from django.core.exceptions import ObjectDoesNotExist
from django.db.models.fields.files import FieldFile
from storages.backends.s3 import S3Storage
from wagtail.models import Collection


logger = logging.getLogger(__name__)


class CollectionDetails(NamedTuple):
    id: int
    path: str
    name: str


class PrivateRootCollectionNotFound(ObjectDoesNotExist):
    pass


class PublicRootCollectionNotFound(ObjectDoesNotExist):
    pass


@lru_cache
def get_root_collection_info() -> dict[str, CollectionDetails]:
    """
    Returns a basic representation of the 'Private' and 'Public' root collections created by a data migration in the
    core app.

    Raises `PrivateRootCollectionNotFound` if the 'Private' collections has not yet been created (or has been deleted).

    Raises `PublicRootCollectionNotFound` if the 'Public' collection has not yet be created (or has been deleted).
    """
    info = {}
    for obj in Collection.objects.filter(depth=2).values_list("id", "path", "name", named=True):
        if "private" not in info and obj.name.lower() == "private":
            info["private"] = obj
        if "public" not in info and obj.name.lower() == "public":
            info["public"] = obj

    if "private" not in info:
        raise PrivateRootCollectionNotFound(
            "The 'Private' Collection cannot be found below 'Root' as expected. Did you forget to run migrations?"
        )
    if "public" not in info:
        raise PublicRootCollectionNotFound(
            "The 'Public' Collection cannot be found below 'Root' as expected. Did you forget to run migrations?"
        )

    return info


def get_private_root_collection_id() -> int:
    return get_root_collection_info()["private"].id


def get_public_root_collection_id() -> int:
    return get_root_collection_info()["public"].id


def get_private_root_collection_path() -> str:
    return get_root_collection_info()["private"].path


def get_public_root_collection_path() -> str:
    return get_root_collection_info()["public"].path


def collection_is_private(collection: Collection) -> bool:
    return collection.path.startswith(get_private_root_collection_path())


def collection_is_public(collection: Collection) -> bool:
    return not collection_is_private(collection)


def set_file_acl(file: FieldFile, acl_name: str) -> bool:
    """
    Set the ACL for the supplied `file` to the supplied `acl_name` value.
    Any exceptions raised during the processed are captured and logged.
    Returns `True` if no errors occured, otherwise `False`.
    """
    if not isinstance(file.storage, S3Storage):
        # In environments that don't use S3, return True immediately,
        # as no futher action is needed, and there's nothing to go wrong!
        logger.info(f"ACL setting is unnecessary for {file.name}")
        return True

    obj = file.storage.bucket.Object(file.name)
    try:
        obj_acl = obj.Acl()
    except ClientError as e:
        logger.debug(f"Failed to retreive ACL for {file.name}: {e!r}")
        return False
    try:
        obj_acl.put(ACL=acl_name)
    except ClientError as e:
        logger.debug(f"Failed to set ACL for {file.name}: {e!r}")
        return False

    logger.info(f"ACL set successfully for {file.name}")
    return True


def set_file_acls(files: Iterable[FieldFile], acl_name: str) -> dict[FieldFile, bool]:
    results: dict[FieldFile, bool] = {}

    def set_file_acl_and_report(file: FieldFile) -> None:
        results[file] = set_file_acl(file, acl_name)

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        executor.map(set_file_acl_and_report, files)

    return results
