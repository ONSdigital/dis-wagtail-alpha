from functools import cached_property

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from django.db import models
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _
from modelcluster.fields import ParentalKey
from wagtail.admin.panels import FieldPanel, FieldRowPanel, InlinePanel, MultiFieldPanel
from wagtail.fields import RichTextField, StreamField
from wagtail.models import Orderable, Page

from ons_alpha.core.models import BasePage
from ons_alpha.release_calendar.blocks import ReleaseStoryBlock
from ons_alpha.utils.models import LinkFields


class ReleaseStatus(models.TextChoices):
    PROVISIONAL = "PROVISIONAL", "Provisional"
    CONFIRMED = "CONFIRMED", "Confirmed"
    CANCELLED = "CANCELLED", "Cancelled"


class ReleaseIndex(BasePage):
    template = "templates/pages/release_index.html"

    parent_page_types = ["home.HomePage"]
    subpage_types = ["ReleasePage"]

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)

        page = request.GET.get("page", 1)

        context["releases"] = Paginator(
            ReleasePage.objects.child_of(self).public().live(),
            settings.DEFAULT_PER_PAGE,
        ).get_page(page)

        return context


class ReleasePageRelatedLink(Orderable, LinkFields):
    """
    Related links. e.g. https://www.ons.gov.uk/releases/welshlanguagecensus2021inwales
    """

    parent = ParentalKey("ReleasePage", related_name="related_links", on_delete=models.CASCADE)


class ReleasePage(BasePage):
    template = "templates/pages/release_page.html"

    parent_page_types = ["ReleaseIndex"]

    status = models.CharField(choices=ReleaseStatus.choices, default=ReleaseStatus.PROVISIONAL, max_length=32)

    summary = RichTextField(features=settings.RICH_TEXT_BASIC)
    # note: this is mocked for the time being. The data would come automatically when the full release
    # is published
    content = StreamField(ReleaseStoryBlock(), blank=True, use_json_field=True)

    release_date = models.DateTimeField()
    next_release = models.CharField(max_length=255, blank=True)

    notice = RichTextField(
        features=settings.RICH_TEXT_BASIC,
        blank=True,
        help_text="Used for data change or cancellation notices. The notice is required when the release is cancelled",
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

    @property
    def is_released(self):
        # cancelled releases should stay the same regardless
        if self.status == ReleaseStatus.CANCELLED:
            return False

        # if tentative or confirmed and the release date has past, treat as released
        return self.release_date <= now()

    @property
    def status_label(self) -> str:
        if self.is_released:
            return _("Published")

        return ReleaseStatus[self.status].label

    def clean(self):
        super().clean()

        if self.status == ReleaseStatus.CANCELLED and not self.notice:
            raise ValidationError({"notice": _("The notice field is required when the release is cancelled")})

    def get_template(self, request, *args, **kwargs):
        if self.status == ReleaseStatus.CANCELLED:
            return "templates/pages/release_page--cancelled.html"

        if not self.is_released:
            return "templates/pages/release_page--upcoming.html"

        return super().get_template(request, *args, **kwargs)

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)

        context["related_links"] = self.related_links_for_context
        context["toc"] = self.toc

        return context

    @cached_property
    def related_links_for_context(self):
        return [
            {
                "text": item.get_link_text(),
                "url": item.get_link_url(),
            }
            for item in self.related_links.select_related("link_page")
        ]

    @cached_property
    def toc(self):
        items = [{"url": "#summary", "text": _("Summary")}]

        if self.is_released:
            for block in self.content:  # pylint: disable=not-an-iterable
                items += block.block.to_table_of_contents_items(block.value)

            if self.contact_details_id:
                items += [{"url": "#contact-details", "text": _("Contact details")}]

        if self.is_accredited:
            items += [{"url": "#about-the-data", "text": _("About the data")}]

        if self.is_released and self.related_links_for_context:
            items += [{"url": "#links", "text": _("You might also be interested in")}]

        return items
