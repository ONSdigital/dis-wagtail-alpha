from django.dispatch import receiver

from wagtail.contrib.frontend_cache.utils import PurgeBatch
from wagtail.signals import page_published, page_unpublished

from .models import InlineIndex, InlineIndexChild


def inlineindex_changed(inlineindex):
    batch = PurgeBatch()
    batch.add_page(inlineindex)
    batch.add_pages(inlineindex.get_children().live())
    batch.purge()


@receiver(page_published, sender=InlineIndex)
def inlineindex_published_handler(instance, **kwargs):
    inlineindex_changed(instance)


@receiver(page_unpublished, sender=InlineIndex)
def inlineindex_deleted_handler(instance, **kwargs):
    inlineindex_changed(instance)


@receiver(page_published, sender=InlineIndexChild)
def inlineindexchild_published_handler(instance, **kwargs):
    inlineindex_changed(instance.get_parent())


@receiver(page_unpublished, sender=InlineIndexChild)
def inlineindexchild_deleted_handler(instance, **kwargs):
    inlineindex_changed(instance.get_parent())
