from functools import cached_property

from django.db import models
from django.db.models import F, QuerySet
from django.db.models.functions import Coalesce
from django.utils.timezone import now
from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel
from wagtail.admin.panels import FieldPanel, FieldRowPanel, InlinePanel
from wagtail.fields import StreamField
from wagtail.models import Orderable, Page
from wagtail.search import index

from ons_alpha.datasets.blocks import DatasetStoryBlock

from .enums import ACTIVE_BUNDLE_STATUSES, EDITABLE_BUNDLE_STATUSES, BundleStatus
from .forms import BundleAdminForm
from .panels import BundleNotePanel, PageChooserWithStatusPanel


class BundlePage(Orderable):
    parent = ParentalKey("Bundle", related_name="bundled_pages", on_delete=models.CASCADE)
    page = models.ForeignKey("wagtailcore.Page", blank=True, null=True, on_delete=models.SET_NULL)

    panels = [
        PageChooserWithStatusPanel(
            "page", ["articles.ArticlePage", "bulletins.BulletinPage", "methodologies.MethodologyPage"]
        ),
    ]

    def __str__(self):
        return f"BundlePage: page {self.page_id} in bundle {self.parent_id}"


class BundlesQuerySet(QuerySet):
    def active(self):
        return self.filter(status__in=ACTIVE_BUNDLE_STATUSES)

    def editable(self):
        return self.filter(status__in=EDITABLE_BUNDLE_STATUSES)


class BundleManager(models.Manager.from_queryset(BundlesQuerySet)):
    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.annotate(
            release_date=Coalesce("publication_date", "release_calendar_page__release_date")
        ).order_by(F("release_date").desc(nulls_last=True), "name", "-pk")
        return queryset


class Bundle(index.Indexed, ClusterableModel):
    base_form_class = BundleAdminForm

    name = models.CharField(max_length=255)
    # note: currently not surfaced, but left here for the time being
    collection_reference = models.CharField(max_length=255, blank=True, help_text="Florence Collection reference")
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

    approved_at = models.DateTimeField(blank=True, null=True)
    approved_by = models.ForeignKey(
        "users.User",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="approved_bundles",
    )
    approved_by.wagtail_reference_index_ignore = True

    publication_date = models.DateTimeField(blank=True, null=True)
    release_calendar_page = models.ForeignKey(
        "release_calendar.ReleasePage",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="bundles",
    )
    status = models.CharField(choices=BundleStatus.choices, default=BundleStatus.PENDING, max_length=32)

    datasets = StreamField(DatasetStoryBlock(), blank=True, use_json_field=True)

    objects = BundleManager()

    panels = [
        FieldPanel("name"),
        FieldRowPanel(
            [
                FieldPanel("release_calendar_page", heading="Release Calendar page"),
                FieldPanel("publication_date", heading="or Publication date"),
            ],
            heading="Scheduling",
            icon="calendar",
        ),
        FieldPanel("status"),
        InlinePanel("bundled_pages", heading="Bundled pages", icon="doc-empty", label="Page"),
        FieldPanel("datasets", help_text="Select the datasets in this bundle.", icon="doc-full"),
        # these are handled by the form
        FieldPanel("approved_by", classname="hidden w-hidden"),
        FieldPanel("approved_at", classname="hidden w-hidden"),
    ]

    search_fields = [
        index.SearchField("name"),
        index.AutocompleteField("name"),
    ]

    def __str__(self):
        return str(self.name)

    @cached_property
    def scheduled_publication_date(self):
        return self.publication_date or (self.release_calendar_page_id and self.release_calendar_page.release_date)

    @property
    def can_be_approved(self):
        # note: strictly speaking, the bundle should in "in review" in order for it to be approved
        return self.status in [BundleStatus.PENDING, BundleStatus.IN_REVIEW]

    def get_bundled_pages(self) -> QuerySet[Page]:
        return Page.objects.filter(pk__in=self.bundled_pages.values_list("page__pk", flat=True))

    def save(self, **kwargs):
        super().save(**kwargs)

        if self.status == BundleStatus.RELEASED:
            return

        if self.scheduled_publication_date and self.scheduled_publication_date >= now():
            # Schedule publishing for related pages
            for bundled_page in self.get_bundled_pages().specific(defer=True):
                if bundled_page.go_live_at == self.scheduled_publication_date:
                    continue

                # note: this could use a custom log action for history
                bundled_page.go_live_at = self.scheduled_publication_date
                revision = bundled_page.save_revision()
                revision.publish()


class BundledPageMixin:
    """
    A helper page mixin for bundled content
    """

    panels = [BundleNotePanel(heading="Bundle", icon="boxes-stacked")]

    @cached_property
    def bundles(self) -> QuerySet[Bundle]:
        if not self.pk:
            return Bundle.objects.none()
        return Bundle.objects.filter(pk__in=self.bundlepage_set.all().values_list("parent", flat=True))

    @cached_property
    def active_bundles(self) -> QuerySet[Bundle]:
        return self.bundles.filter(status__in=ACTIVE_BUNDLE_STATUSES)

    @cached_property
    def in_active_bundle(self) -> bool:
        return self.bundlepage_set.filter(parent__status__in=ACTIVE_BUNDLE_STATUSES).exists()

    @property
    def active_bundle(self) -> Bundle:
        return self.active_bundles.first()
