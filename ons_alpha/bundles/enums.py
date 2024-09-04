from django.db import models


class BundleStatus(models.TextChoices):
    PENDING = "PENDING", "Pending"
    IN_REVIEW = "IN_REVIEW", "In Review"
    APPROVED = "APPROVED", "Approved"
    RELEASED = "RELEASED", "Released"


ACTIVE_BUNDLE_STATUSES = [BundleStatus.PENDING, BundleStatus.IN_REVIEW, BundleStatus.APPROVED]
EDITABLE_BUNDLE_STATUSES = [BundleStatus.PENDING, BundleStatus.IN_REVIEW]
