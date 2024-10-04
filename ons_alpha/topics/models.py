from functools import cached_property
from typing import Type

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import OuterRef, QuerySet, Subquery
from django.utils.functional import classproperty
from django.utils.text import slugify
from django.utils.translation import gettext as _
from wagtail.admin.panels import FieldPanel, ObjectList, TabbedInterface
from wagtail.models import Page
from wagtail.search import index

from ons_alpha.articles.models import ArticlePage, ArticleSeriesPage
from ons_alpha.bulletins.models import BulletinPage, BulletinSeriesPage
from ons_alpha.core.blocks import (
    DocumentListBlock,
    FeaturedDocumentBlock,
    HeadlineFiguresBlock,
)
from ons_alpha.core.models.base import BasePage
from ons_alpha.core.models.mixins import SubpageMixin
from ons_alpha.methodologies.models import MethodologyPage
from ons_alpha.taxonomy.models import Topic
from ons_alpha.utils.fields import StreamField


class BaseTopicPage(SubpageMixin, BasePage):
    topic = models.ForeignKey(
        Topic,
        on_delete=models.SET_NULL,
        null=True,
        blank=False,
        related_name="%(class)s",
        # '%(class)s' is replaced by the lowercased name of the child class that the field is used in.
        # https://docs.djangoproject.com/en/5.0/topics/db/models/#be-careful-with-related-name-and-related-query-name
    )

    summary = models.TextField(blank=True)

    content_panels = BasePage.content_panels + [FieldPanel("summary")]

    @classproperty
    def edit_handler(cls):
        return TabbedInterface(
            [
                ObjectList(cls.content_panels, heading="Content"),
                ObjectList(
                    [FieldPanel("topic")],
                    help_text="Select the topics that this page relates to.",
                    heading="Taxonomy",
                ),
                ObjectList(BasePage.promote_panels, heading="Promote"),
            ]
        )

    class Meta:
        abstract = True

    def clean(self):
        super().clean()

        for sub_page_type in BaseTopicPage.__subclasses__():
            # Find other pages (and translations) for this topic.
            # Translations of the same page are allowed, but other pages aren't.
            if sub_page_type.objects.filter(topic=self.topic).exclude(translation_key=self.translation_key).exists():
                raise ValidationError({"topic": "Topic Page (or Section) with this topic already exists."})


class TopicPage(BaseTopicPage):
    template = "templates/pages/topics/topic_page.html"
    parent_page_types = ["topics.TopicSectionPage"]
    subpage_types = [
        "articles.ArticleSeriesPage",
        "bulletins.BulletinSeriesPage",
        "methodologies.MethodologyPage",
    ]
    page_description = "A specific topic page. e.g. Public sector finance or Inflation and price indices"

    headline_figures = StreamField([("figures", HeadlineFiguresBlock())], blank=True)
    body = StreamField(
        [
            ("featured_document", FeaturedDocumentBlock()),
            ("document_list", DocumentListBlock()),
        ],
        blank=True,
        block_counts={
            "featured_document": {"max_num": 1},
        },
    )

    content_panels = BasePage.content_panels + [
        FieldPanel("summary"),
        FieldPanel("headline_figures"),
        FieldPanel("body"),
    ]

    search_fields = BasePage.search_fields + [
        index.SearchField("summary"),
        index.SearchField("headline_figures"),
        index.SearchField("body"),
    ]

    def latest_by_series(self, model: Type[Page], series_model: Type[Page], topic: Topic = None) -> QuerySet:
        newest_qs = (
            model.objects.live().public().filter(path__startswith=OuterRef("path"), depth__gte=OuterRef("depth"))
        )
        if topic:
            newest_qs = newest_qs.filter(topics__topic=topic)
        newest_qs = newest_qs.order_by("-release_date")

        model_pk_qs = series_model.objects.not_child_of(self) if topic else series_model.objects.child_of(self)
        return model.objects.filter(
            pk__in=model_pk_qs.annotate(latest_child_page=Subquery(newest_qs.values("pk")[:1])).values_list(
                "latest_child_page", flat=True
            )
        ).order_by("-release_date")

    @cached_property
    def latest_bulletins(self) -> QuerySet[BulletinPage]:
        return self.latest_by_series(BulletinPage, BulletinSeriesPage)

    @cached_property
    def latest_articles(self) -> QuerySet[ArticlePage]:
        return self.latest_by_series(ArticlePage, ArticleSeriesPage)

    @cached_property
    def latest_methodologies(self) -> QuerySet[MethodologyPage]:
        return MethodologyPage.objects.live().public().child_of(self).order_by("-last_revised_date", "-pk")[:5]

    @cached_property
    def related_by_topic(self) -> dict[str, QuerySet]:
        related = {}
        if bulletins := self.latest_by_series(BulletinPage, BulletinSeriesPage, self.topic):
            related[_("Bulletins")] = bulletins

        if articles := self.latest_by_series(ArticlePage, ArticleSeriesPage, self.topic):
            related[_("Articles")] = articles

        methodologies_qs = (
            MethodologyPage.objects.live()
            .public()
            .not_child_of(self)
            .filter(topics__topic=self.topic)
            .order_by("-last_revised_date", "-pk")
        )
        if methodologies := methodologies_qs:
            related[_("Methodologies")] = methodologies

        return related

    @cached_property
    def sections(
        self,
    ) -> dict[str, QuerySet[BulletinPage | ArticlePage | MethodologyPage]]:
        sections_dict = {}
        if bulletins := self.latest_bulletins:
            sections_dict[_("Statistical bulletins")] = bulletins

        if articles := self.latest_articles:
            sections_dict[_("Articles")] = articles

        if methodologies := self.latest_methodologies:
            sections_dict[_("Methodologies")] = methodologies

        return sections_dict

    @cached_property
    def toc(self) -> list[dict[str, str]]:
        items = []

        # When related content is specified manually, use it to generate the TOC,
        # and return early to prevent unnecessary lookups
        if self.body:
            for block in self.body:  # pylint: disable=not-an-iterable,useless-suppression
                if hasattr(block.block, "to_table_of_contents_items"):
                    items += block.block.to_table_of_contents_items(block.value)
                # Return the list to terminate here
                return items

        # Generate the TOC automatically (via topic association)
        for title in self.sections:
            items.append({"url": f"#{slugify(title)}", "text": title})
        if self.related_by_topic:
            items.append({"url": "#related", "text": _("Related content")})
        return items


class TopicSectionPage(BaseTopicPage):
    template = "templates/pages/topics/topic_section_page.html"
    subpage_types = ["topics.TopicSectionPage", "topics.TopicPage"]
    page_description = "General topic page. e.g. Economy"
