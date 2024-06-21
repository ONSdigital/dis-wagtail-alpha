from collections.abc import Mapping
from typing import Any, Union

from django.db import models
from django.http.request import HttpRequest
from django.utils.functional import cached_property

from wagtail.admin.panels import FieldPanel, InlinePanel
from wagtail.models import Page
from wagtail.query import PageQuerySet
from wagtail.search import index

from ons_alpha.core.blocks import StoryBlock
from ons_alpha.core.models import BasePage
from ons_alpha.utils.fields import StreamField


class BaseInlineIndexPage(BasePage):
    """
    Base class for the `InlineIndex` and `InlineIndexChild` page types.
    Includes some functionality that is shared between page types, as
    well as a few methods that must be overridden for each.
    """

    class Meta:
        abstract = True

    def __str__(self) -> str:
        return self.content_title

    @property
    def index_page(self) -> "InlineIndex":
        raise NotImplementedError

    @property
    def content_title(self) -> str:
        raise NotImplementedError

    @property
    def index_title(self) -> str:
        return self.index_page.title

    def get_index_page_children(
        self,
        after: "InlineIndexChild" = None,
        before: "InlineIndexChild" = None,
    ) -> PageQuerySet:
        """
        Return a `PageQuerySet` of pages that are children of the
        index page, automatically filtered to include only live
        pages depending on the value of `self._include_draft_children`
        (set in `BaseInlineIndexPage.get_context()`).

        If `after` is provided, the result will only include
        pages that appear AFTER that page in the tree.

        If `before` is provided, the result will only include
        pages that appear BEFORE that page in the tree.

        NOTE: This will give the same result for the index page and any child
        pages, because we are going through `self.index_page`.
        """
        if before:
            queryset = before.get_prev_siblings()
        elif after:
            queryset = after.get_next_siblings()
        else:
            queryset = self.index_page.get_children()

        if not getattr(self, "_include_draft_children", False):
            queryset = queryset.live()

        return queryset.exact_type(InlineIndexChild)

    def get_contents(self) -> PageQuerySet:
        """
        Return a queryset of all pages needed to render the table of contents.

        NOTE: This will give the same result for the index page and any child
        pages, because we are going through `self.index_page`.
        """
        queryset = Page.objects.page(self.index_page) | self.get_index_page_children()
        return queryset.specific()

    def get_next_page(self) -> "InlineIndexChild | None":
        """
        Subclasses must override this method if they need
        to return something other than `None`.
        """
        return None

    def get_prev_page(self) -> Union["InlineIndex", "InlineIndexChild"] | None:
        """
        Subclasses must override this method if they need
        to return something other than `None`.
        """
        return None

    def draft_for_page_available(self) -> bool:
        return self.has_unpublished_changes or not self.live

    def viewing_page_draft(self, request: HttpRequest) -> bool:
        """
        Allows the editor to prepare an entire "inline index" section (the
        index page with the children) in draft mode but also be able to see
        how the table of contents and the navigation will appear.
        """
        return request.is_preview and self.draft_for_page_available()

    def get_context(self, request: HttpRequest) -> Mapping[str, Any]:
        context = super().get_context(request)

        # This is picked up by get_index_page_children() to
        # include/exclude draft pages accordingly.
        self._include_draft_children = self.viewing_page_draft(request)

        context["index"] = self.get_contents()
        context["next_page"] = self.get_next_page()
        context["prev_page"] = self.get_prev_page()
        return context


class InlineIndex(BaseInlineIndexPage):
    """A page with an included table of contents, listing this page and its children.

    InlineIndex and InlineIndexChild can be used to build a "guide" to a service or
    topic. All of the pages are shown together in a flat hierarchy in the table of
    contents, with the index page shown as the first sibling. The "next" and "previous"
    buttons navigate through the guide.

    See e.g. https://www.gov.uk/attendance-allowance for the GDS pattern that this
    implements.
    """

    template = "pages/inlineindex/inline_index_page.html"

    subtitle = models.CharField(
        max_length=255,
        help_text="Title that appears on the index. (e.g. Introduction)",
        default="Introduction",
    )

    body = StreamField(StoryBlock(), use_json_field=True)

    subpage_types = ["inlineindex.InlineIndexChild"]

    search_fields = BasePage.search_fields + [
        index.SearchField("subtitle"),
        index.SearchField("body"),
    ]

    content_panels = BasePage.content_panels + [
        FieldPanel("subtitle"),
        FieldPanel("body"),
        InlinePanel("page_related_pages", label="Related pages"),
    ]

    @property
    def content_title(self) -> str:
        return self.subtitle

    @cached_property
    def index_page(self) -> "InlineIndex":
        return self

    def get_next_page(self) -> "InlineIndexChild | None":
        """Return the first child.

        The index page is displayed as the first sibling in the table of contents.
        The next page is actually the first child in the page tree.
        """
        return self.get_index_page_children().first()


class InlineIndexChild(BaseInlineIndexPage):
    template = InlineIndex.template

    body = StreamField(StoryBlock(), use_json_field=True)

    parent_page_types = ["inlineindex.InlineIndex"]

    subpage_types = ["standardpages.InformationPage"]

    search_fields = BasePage.search_fields + [
        index.SearchField("body"),
    ]

    content_panels = BasePage.content_panels + [
        FieldPanel("body"),
    ]

    @property
    def content_title(self) -> str:
        """Overrides InlineIndex.content_title to return the title of this page."""
        return self.title

    @cached_property
    def index_page(self) -> InlineIndex:
        return (
            InlineIndex.objects.parent_of(self)
            .prefetch_related("page_related_pages")
            .get()
        )

    @cached_property
    def related_pages(self) -> PageQuerySet:
        return self.index_page.related_pages

    def get_next_page(self) -> "InlineIndexChild | None":
        """Return the next sibling, if there is one. NB this is implemented
        differently on InlineIndex.
        """
        next_siblings = self.get_index_page_children(after=self)

        next_sibling = next_siblings.first()
        if next_sibling is not None:
            return next_sibling.specific

        return None

    def get_prev_page(self) -> Union["InlineIndexChild", InlineIndex] | None:
        """Return the previous sibling, or in the case of a first child, the
        parent. NB this method is not implemented on InlineIndex, so the
        template just gets None.
        """
        prev_siblings = self.get_index_page_children(before=self)

        prev_sibling = prev_siblings.first() or self.index_page
        if prev_sibling is not None:
            return prev_sibling.specific

        return None
