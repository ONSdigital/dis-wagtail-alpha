from django.db import models
from wagtail.images.models import AbstractImage, Image

from ons_alpha.private_media.models import PrivateAbstractRendition, PrivateImageMixin


class CustomImage(PrivateImageMixin, AbstractImage):
    admin_form_fields = Image.admin_form_fields


class Rendition(PrivateAbstractRendition):
    image = models.ForeignKey("CustomImage", related_name="renditions", on_delete=models.CASCADE)

    class Meta:
        unique_together = (("image", "filter_spec", "focal_point_key"),)
