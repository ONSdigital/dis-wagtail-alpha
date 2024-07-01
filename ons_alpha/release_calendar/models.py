from django.conf import settings
from django.db import models
from modelcluster.fields import ParentalKey
from wagtail.admin.panels import FieldPanel, FieldRowPanel, InlinePanel, MultiFieldPanel
from wagtail.fields import RichTextField, StreamField
from wagtail.models import Orderable, Page

from ons_alpha.core.models import BasePage
from ons_alpha.release_calendar.blocks import ReleaseStoryBlock
from ons_alpha.utils.models import LinkFields


class ReleaseStatus(models.TextChoices):
    UPCOMING = "UPCOMING", "Upcoming"
    PUBLISHED = "PUBLISHED", "Published"
    CANCELLED = "CANCELLED", "Cancelled"


class ReleaseIndex(BasePage):
    template = "templates/pages/release_index.html"

    parent_page_types = ["home.HomePage"]
    subpage_types = ["ReleasePage"]

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)

        context["releases"] = ReleasePage.objects.child_of(self).public().live()

        return context


class ReleasePageRelatedLink(Orderable, LinkFields):
    """
    Related links. e.g. https://www.ons.gov.uk/releases/welshlanguagecensus2021inwales
    """

    parent = ParentalKey(
        "ReleasePage", related_name="related_links", on_delete=models.CASCADE
    )


class ReleasePage(BasePage):
    template = "templates/pages/release_page.html"

    parent_page_types = ["ReleaseIndex"]

    status = models.CharField(
        choices=ReleaseStatus.choices, default=ReleaseStatus.UPCOMING, max_length=32
    )

    summary = RichTextField(features=settings.RICH_TEXT_BASIC)
    # note: this is mocked for the time being. The data would come automatically when the full release
    # is published
    content = StreamField(ReleaseStoryBlock(), blank=True, use_json_field=True)

    release_date = models.DateTimeField()
    next_release = models.CharField(max_length=255, blank=True)

    notice = RichTextField(
        features=settings.RICH_TEXT_BASIC,
        blank=True,
        help_text="Used for data change or cancellation notices",
    )
    contact_details = models.ForeignKey(
        "core.ContactDetails",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    is_accredited = models.BooleanField("Accredited Official Statistics", default=False)

    content_panels = Page.content_panels + [
        MultiFieldPanel(
            [
                FieldRowPanel(
                    [FieldPanel("release_date"), FieldPanel("next_release")],
                    heading="Dates",
                ),
                FieldPanel("status"),
                FieldPanel("notice"),
                FieldPanel("is_accredited"),
            ],
            heading="Metadata",
        ),
        FieldPanel("summary"),
        FieldPanel("content"),
        FieldPanel("contact_details"),
        InlinePanel("related_links", heading="Related links"),
    ]
