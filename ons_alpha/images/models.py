from typing import NamedTuple

from django.core.files.base import ContentFile
from django.db import models
from wagtail.images.models import AbstractImage, AbstractRendition, Image


class StubImage(NamedTuple):
    """
    A stub image class for use when generating rendition image URLs.
    """

    id: int

    @property
    def file(self):
        # HACK: Provide a blank filename to satisfy `reverse`,
        # but the view never uses it.
        return ContentFile("", name="")


class CustomImage(AbstractImage):
    admin_form_fields = Image.admin_form_fields


class Rendition(AbstractRendition):
    image = models.ForeignKey("CustomImage", related_name="renditions", on_delete=models.CASCADE)

    class Meta:
        unique_together = (("image", "filter_spec", "focal_point_key"),)

    @property
    def media_url(self):
        return super().url

    @property
    def url(self):
        """
        Redirect uses of the rendition to a view which checks permissions.
        """
        from wagtail.images.views.serve import generate_image_url  # pylint: disable=import-outside-toplevel

        return generate_image_url(StubImage(self.image_id), self.filter_spec)
