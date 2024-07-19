from functools import cached_property
from typing import Dict, List

from django.db import models
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from modelcluster.fields import ParentalKey
from wagtail.admin.panels import (
    FieldPanel,
    FieldRowPanel,
    HelpPanel,
    MultiFieldPanel,
    MultipleChooserPanel,
    ObjectList,
    TabbedInterface,
)
from wagtail.contrib.routable_page.models import RoutablePageMixin, path
from wagtail.fields import StreamField
from wagtail.models import Orderable, Page, Revision
from wagtail.search import index

from ons_alpha.core.models.base import BasePage

from .blocks import BulletinStoryBlock, CorrectionsNoticesStoryBlock


# Import BulletinPageAdminForm lazily to avoid circular import
BulletinPageAdminForm = None


class BulletinTopicRelationship(Orderable):
    page = ParentalKey("bulletins.BulletinPage", on_delete=models.CASCADE, related_name="topics")
    topic = models.ForeignKey("taxonomy.Topic", on_delete=models.CASCADE, related_name="bulletins")


class BulletinPage(BasePage):
    base_form_class = BulletinPageAdminForm  # Reference the form here
    template = "templates/pages/bulletins/bulletin_page.html"
    parent_page_types = ["BulletinSeriesPage"]

    summary = models.TextField()
    release_date = models.DateField()
    next_release_date = models.DateField()
    contact_details = models.ForeignKey(
        "core.ContactDetails",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    is_accredited = models.BooleanField(default=False)
    body = StreamField(BulletinStoryBlock(), use_json_field=True)
    updates = StreamField(CorrectionsNoticesStoryBlock(), blank=True, use_json_field=True)

    content_panels = BasePage.content_panels + [
        FieldPanel("summary"),
        MultiFieldPanel(
            [
                FieldRowPanel(
                    [
                        FieldPanel("release_date"),
                        FieldPanel("next_release_date"),
                    ]
                ),
                FieldPanel("is_accredited"),
                FieldPanel("contact_details"),
            ],
            heading="Metadata",
        ),
        FieldPanel("body"),
    ]

    edit_handler = TabbedInterface(
        [
            ObjectList(content_panels, heading="Content"),
            ObjectList(
                [
                    MultipleChooserPanel("topics", label="Topic", chooser_field_name="topic"),
                ],
                help_text="Select the topics that this bulletin relates to.",
                heading="Taxonomy",
            ),
            ObjectList(
                [FieldPanel("updates", help_text="Add any corrections or updates")], heading="Corrections & Updates"
            ),
            ObjectList(BasePage.promote_panels, heading="Promote"),
            ObjectList(BasePage.settings_panels, heading="Settings", classname="settings"),
        ]
    )

    search_fields = BasePage.search_fields + [
        index.SearchField("summary"),
        index.SearchField("body"),
        index.SearchField("get_admin_display_title", boost=2),
        index.AutocompleteField("get_admin_display_title"),
    ]

    @property
    def full_title(self):
        return f"{self.get_parent().title}: {self.title}"

    @property
    def is_latest(self):
        latest_id = (
            BulletinPage.objects.sibling_of(self).live().order_by("-release_date").values_list("id", flat=True).first()
        )
        return self.pk == latest_id

    @cached_property
    def toc(self) -> List[Dict[str, str]]:
        items = [{"url": "#summary", "text": "Summary"}]
        for block in self.body:  # pylint: disable=not-an-iterable
            if hasattr(block.block, "to_table_of_contents_items"):
                items += block.block.to_table_of_contents_items(block.value)
        if self.contact_details_id:
            items += [{"url": "#contact-details", "text": "Contact details"}]
        return items

    def get_admin_display_title(self):
        # tweak the admin display title to include the parent title
        return f"{self.get_parent().title}: {self.draft_title or self.title}"

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        context["toc"] = self.toc
        return context


class BulletinSeriesPage(RoutablePageMixin, Page):
    parent_page_types = ["topics.TopicPage"]
    subpage_types = ["BulletinPage"]
    preview_modes = []  # Disabling the preview mode due to it being a container page.
    page_description = "A container for Bulletin series"

    content_panels = Page.content_panels + [
        HelpPanel(
            content="This is a container for the Bulletin series. It provides the <code>/latest</code>,"
            "<code>/previous-release</code> evergreen paths, as well as the actual bulletins. "
            "Add a new Bulletin page under this container. Note: for the purpose of this "
            "proof of concept, we only look at published Bulletin pages to power the view "
            "previous/view latest behaviour"
        )
    ]

    def get_latest_bulletin(self):
        return BulletinPage.objects.live().child_of(self).order_by("-release_date").first()

    @path("")
    def index(self, request):
        # Redirect to /latest as this is a container page without its own content
        return redirect(self.get_url(request) + self.reverse_subpage("latest_bulletin"))

    @path("latest/")
    def latest_bulletin(self, request):
        latest = self.get_latest_bulletin()
        if not latest:
            raise Http404

        return self.render(request, context_overrides={"page": latest})

    @path("previous-releases/")
    def previous_releases(self, request):
        previous = BulletinPage.objects.live().child_of(self).order_by("-release_date")
        return self.render(
            request,
            context_overrides={"bulletins": previous},
            template="templates/pages/bulletins/previous_releases.html",
        )

    @path("previous/v<int:version>/")
    def previous_version(self, request, version):
        page_revision = get_object_or_404(Revision, pk=version)

        # Ensure the revision is of the correct page type and is published
        page = page_revision.as_page_object()
        if not isinstance(page, BulletinPage) or not page.live:
            raise Http404

        return self.render(request, context_overrides={"page": page})
