from functools import cached_property

from django.conf import settings
from django.db import models
from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel
from wagtail.admin.panels import FieldPanel, FieldRowPanel, InlinePanel, PageChooserPanel
from wagtail.fields import RichTextField
from wagtail.models import Orderable
from wagtail.search import index


class BundleStatus(models.TextChoices):
    PENDING = "PENDING", "Pending"
    IN_REVIEW = "IN_REVIEW", "In Review"
    APPROVED = "APPROVED", "Approved"
    RELEASED = "RELEASED", "Released"


ACTIVE_BUNDLE_STATUSES = [BundleStatus.PENDING, BundleStatus.IN_REVIEW]


class BundlePage(Orderable):
    parent = ParentalKey("Bundle", related_name="bundled_pages", on_delete=models.CASCADE)
    page = models.ForeignKey("wagtailcore.Page", blank=True, null=True, on_delete=models.SET_NULL)

    panels = [
        PageChooserPanel("page", ["bulletins.BulletinPage"]),
    ]


class BundleLink(Orderable):
    parent = ParentalKey("Bundle", related_name="bundled_links", on_delete=models.CASCADE)
    url = models.URLField(blank=True)
    title = models.CharField(blank=True, max_length=255)
    description = RichTextField(blank=True, features=settings.RICH_TEXT_BASIC)

    panels = [
        FieldPanel("url", heading="URL"),
        FieldPanel("title"),
        FieldPanel("description"),
    ]


class ActiveBundlesManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(status__in=ACTIVE_BUNDLE_STATUSES)


class Bundle(index.Indexed, ClusterableModel):
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

    objects = models.Manager()
    active_objects = ActiveBundlesManager()

    panels = [
        FieldPanel("name"),
        FieldPanel("topic", icon="tag"),
        FieldPanel("collection_reference"),
        FieldRowPanel(
            [
                FieldPanel("publication_date"),
                FieldPanel("release_calendar_page", heading="or Release Calendar page"),
            ],
            heading="Scheduling",
            icon="calendar",
        ),
        FieldPanel("status"),
        InlinePanel("bundled_pages", heading="Bundled pages", icon="doc-empty"),
        InlinePanel("bundled_links", heading="Bundled links (datasets, time series)", icon="link"),
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
