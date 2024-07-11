from functools import cached_property

from django.db import models
from django.shortcuts import redirect, render
from wagtail.admin.panels import FieldPanel, FieldRowPanel, MultiFieldPanel, ObjectList, TabbedInterface
from wagtail.contrib.routable_page.models import RoutablePageMixin, path
from wagtail.models import Page

from ons_alpha.core.models.base import BasePage
from ons_alpha.utils.fields import StreamField

from .blocks import BulletinStoryBlock, CorrectionsNoticesStoryBlock


class BulletinPage(BasePage):
    template = "templates/pages/bulletins/bulletin_page.html"
    parent_page_types = ["topics.TopicPage"]

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
                [FieldPanel("updates", help_text="Add any corrections or updates")], heading="Corrections & Updates"
            ),
            ObjectList(BasePage.promote_panels, heading="Promote"),
            ObjectList(BasePage.settings_panels, heading="Settings", classname="settings"),
        ]
    )

    @property
    def is_latest(self):
        latest_id = (
            BulletinPage.objects.sibling_of(self).live().order_by("-release_date").values_list("id", flat=True).first()
        )
        return self.pk == latest_id

    @cached_property
    def toc(self):
        items = [{"url": "#summary", "text": "Summary"}]
        for block in self.body:  # pylint: disable=not-an-iterable
            if hasattr(block.block, "to_table_of_contents_items"):
                items += block.block.to_table_of_contents_items(block.value)
        if self.contact_details_id:
            items += [{"url": "#contact-details", "text": "Contact details"}]
        return items

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        context["toc"] = self.toc
        return context


class BulletinSeriesPage(RoutablePageMixin, Page):
    template = "templates/pages/bulletins/series_page.html"
    parent_page_types = ["home.HomePage"]
    subpage_types = ["BulletinPage"]
    preview_modes = []  # Disabling the preview mode due to it being a container page.

    def get_latest_bulletin(self):
        return BulletinPage.objects.live().child_of(self).order_by("-release_date").first()

    @path("latest/")
    def latest_bulletin(self, request):
        latest = self.get_latest_bulletin()
        return render(request, "templates/pages/bulletins/bulletin_page.html", {"page": latest})

    @path("previous-releases/")
    def previous_releases(self, request):
        previous = BulletinPage.objects.live().child_of(self).order_by("-release_date")
        return render(request, "templates/pages/bulletins/previous_releases.html", {"bulletins": previous})

    def serve(self, request, *args, **kwargs):
        # Re-directing to the latest bulletin
        return redirect(self.get_url(request) + self.reverse_subpage("latest_bulletin"))
