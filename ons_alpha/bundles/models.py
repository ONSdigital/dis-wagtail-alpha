from functools import cached_property

from django.db import models
from wagtail.admin.panels import FieldPanel, FieldRowPanel
from wagtail.search import index


class BundleStatus(models.TextChoices):
    PENDING = "PENDING", "Pending"
    IN_REVIEW = "IN_REVIEW", "In Review"
    APPROVED = "APPROVED", "Approved"
    RELEASED = "RELEASED", "Released"


class Bundle(index.Indexed, models.Model):
    name = models.CharField(max_length=255)
    collection_reference = models.CharField(max_length=255, blank=True, help_text="Florence Collection reference")
    topic = models.ForeignKey(
        "topics.TopicPage",
        null=True,
        on_delete=models.SET_NULL,
        related_name="bundles",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        "users.User",
        null=True,
        blank=True,
        editable=True,
        on_delete=models.SET_NULL,
        related_name="bundles",
    )
    created_by.wagtail_reference_index_ignore = True

    publication_date = models.DateTimeField(blank=True, null=True)
    release_calendar_page = models.ForeignKey(
        "release_calendar.ReleasePage",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="bundles",
    )
    status = models.CharField(choices=BundleStatus.choices, default=BundleStatus.PENDING, max_length=32)

    panels = [
        FieldPanel("name"),
        FieldPanel("topic"),
        FieldPanel("collection_reference"),
        FieldRowPanel(
            [
                FieldPanel("publication_date"),
                FieldPanel("release_calendar_page", heading="or Release Calendar page"),
            ],
            heading="Scheduling",
        ),
        FieldPanel("status"),
    ]

    search_fields = [
        index.SearchField("name"),
        index.AutocompleteField("name"),
    ]

    def __str__(self):
        return self.name

    @cached_property
    def scheduled_publication_date(self):
        return self.publication_date or self.release_calendar_page.release_date
