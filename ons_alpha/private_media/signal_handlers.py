from collections import defaultdict

from django.apps import apps
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q, QuerySet
from wagtail.images.models import AbstractImage
from wagtail.models import Page, ReferenceIndex
from wagtail.signals import page_published, page_unpublished

from .models import PrivateMediaCollectionMember


def get_private_media_models():
    return [m for m in apps.get_models() if issubclass(m, PrivateMediaCollectionMember)]


def publish_page_media_on_publish(instance, **kwargs):  # pylint: disable=unused-argument
    """
    Signal handler to be connected to the 'page_published' signal for
    all page types. It is responsible for identifying any privacy-controlled
    media used by the page, and ensuring that it is also made public.
    """
    ids_by_ctype = defaultdict(list)
    for ct_id, obj_id in get_all_page_media_ids(instance):
        ids_by_ctype[ct_id].append(obj_id)

    for ct_id, id_list in ids_by_ctype.items():
        model_class = ContentType.objects.get_for_id(ct_id).model_class()
        id_list = [model_class._meta.pk.to_python(id) for id in id_list]
        private_objects_qs = model_class.objects.filter(id__in=id_list, is_private=True).select_related(
            "collection", "last_public_collection", "last_private_collection"
        )
        if issubclass(model_class, AbstractImage):
            private_objects_qs = private_objects_qs.prefetch_related("renditions")
        model_class.objects.bulk_make_public(list(private_objects_qs))


def unpublish_page_media_on_unpublish(instance, **kwargs):  # pylint: disable=unused-argument
    """
    Signal handler to be connected to the 'page_unpublished' signal for
    all page types. It is responsible for identifying any privacy-controlled
    media used exclusively by the page, and ensuring that it is also made
    private.
    """
    ids_by_ctype = defaultdict(list)
    for ct_id, obj_id in get_unique_to_page_media_ids(instance):
        ids_by_ctype[ct_id].append(obj_id)

    for ct_id, id_list in ids_by_ctype.items():
        model_class = ContentType.objects.get_for_id(ct_id).model_class()
        id_list = [model_class._meta.pk.to_python(id) for id in id_list]
        public_objects_qs = model_class.objects.filter(id__in=id_list, is_private=False).select_related(
            "collection", "last_public_collection", "last_private_collection"
        )
        if issubclass(model_class, AbstractImage):
            public_objects_qs = public_objects_qs.prefetch_related("renditions")
        model_class.objects.bulk_make_private(list(public_objects_qs))


def register_signal_handlers():
    page_published.connect(publish_page_media_on_publish, dispatch_uid="publish_media")
    page_unpublished.connect(unpublish_page_media_on_unpublish, dispatch_uid="unpublish_media")


def get_media_references(page: Page) -> QuerySet[ReferenceIndex]:
    """
    Return a queryset of `ReferenceIndex` entries for the provided `page`
    `Page`, which refer to images, documents or instances of other model classe that
    subclass `PrivateMediaCollectionMember`.
    """
    models = get_private_media_models()
    content_types = ContentType.objects.get_for_models(*models)
    return ReferenceIndex.get_references_for_object(page).filter(to_content_type__in=content_types.values())


def get_all_page_media_ids(page: Page) -> set[tuple[str, str]]:
    """
    Return a set of (`content_type_id`, `object_id`) tuples for all media referenced
    by the provided `Page`.
    """
    return set(get_media_references(page).values_list("to_content_type", "to_object_id").distinct())


def get_unique_to_page_media_ids(page) -> set[tuple[str, str]]:
    """
    Return a set of (`content_type_id`, `object_id`) tuples for media referenced
    ONLY by the provided `Page` (similar to `get_all_page_media_ids()`, but
    excluding media used on other pages).
    """
    page_ctype = ContentType.objects.get_for_model(Page)
    all_identifiers = get_all_page_media_ids(page)
    all_identifiers_q = Q()
    for ct_id, obj_id in all_identifiers:
        all_identifiers_q |= Q(to_content_type_id=ct_id, to_object_id=obj_id)

    referenced_elsewhere_identifiers = {
        ReferenceIndex.objects.filter(all_identifiers_q)
        .filter(base_content_type=page_ctype)
        .exclude(object_id=page.id)
        .values_list("to_content_type", "to_object_id")
        .distinct()
    }
    return all_identifiers - referenced_elsewhere_identifiers
