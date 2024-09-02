from django.core.exceptions import ValidationError
from django.db import models
from wagtail.admin.panels import (
    FieldPanel,
    ObjectList,
    TabbedInterface)

from ons_alpha.core.models.base import BasePage
from ons_alpha.core.models.mixins import SubpageMixin
from ons_alpha.taxonomy.models import Topic


class BaseTopicPage(SubpageMixin, BasePage):
    topic = models.OneToOneField(
        Topic,
        on_delete=models.SET_NULL,
        null=True,
        blank=False,
        related_name="%(class)s",
        # '%(class)s' is replaced by the lowercased name of the child class that the field is used in.
        # https://docs.djangoproject.com/en/5.0/topics/db/models/#be-careful-with-related-name-and-related-query-name
    )

    content_panels = BasePage.content_panels

    edit_handler = TabbedInterface(
        [
            ObjectList(content_panels, heading="Content"),
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


class TopicPage(BaseTopicPage):
    template = "templates/pages/topics/topic_page.html"
    parent_page_types = ["topics.TopicSectionPage"]
    subpage_types = ["articles.ArticleSeriesPage", "bulletins.BulletinSeriesPage", "methodologies.MethodologyPage"]
    page_description = "A specific topic page. e.g. Public sector finance or Inflation and price indices"
    page_summary = models.CharField(blank=True, max_length=255)
    # The topics page has a list of all child and tagged pages this is a list of all the types of page that
    # links to the position for that page type in the list
    topic_page_nav = models.CharField(blank=True, max_length=255)

    content_panels = BasePage.content_panels + [
        FieldPanel("page_summary"),
        FieldPanel("topic_page_nav"),
    ]

    edit_handler = TabbedInterface(
        [
            ObjectList(content_panels, heading="Content"),
            ObjectList(
                [FieldPanel("topic")],
                help_text="Select the topics that this page relates to.",
                heading="Taxonomy",
            ),
            ObjectList(BasePage.promote_panels, heading="Promote"),
        ]
    )

    def clean(self):
        super().clean()
        if TopicSectionPage.objects.filter(topic=self.topic).exists():
            raise ValidationError({"topic": "Topic Section Page with this topic already exists."})

    def topic_list(self):
        menu_items = self.get_children().live().public().specific()
        display_names = []
        for m in menu_items:
            display_names.append(m.specific.page_type_display_name )
        return sorted(set(display_names))

    def subpage_list(self):
        menu_items = self.topic_list()
        display_names = {}
        for menu_item in menu_items:
            display_names[menu_item] = []
            subpage_list = []
            for subpage in self.get_children().live().public().specific():
                if subpage.specific.page_type_display_name == menu_item:
                    if len(subpage.get_children().live().public().specific()) > 0:
                        for childpage in subpage.get_children().live().public().specific():
                            subpage_list.append(childpage)
                    else:
                        subpage_list.append(subpage)
                display_names[menu_item] = subpage_list
        return display_names

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        context["topic_list"] = self.topic_list()
        context["subpage_dict"] = self.subpage_list()
        return context


class TopicSectionPage(BaseTopicPage):
    template = "templates/pages/topics/topic_section_page.html"
    subpage_types = ["topics.TopicSectionPage", "topics.TopicPage"]
    page_description = "General topic page. e.g. Economy"
    summary = models.CharField(blank=True, max_length=255)

    content_panels = BasePage.content_panels + [
            FieldPanel("summary"),
        ]

    edit_handler = TabbedInterface(
        [
            ObjectList(content_panels, heading="Content"),
            ObjectList(
                [FieldPanel("topic")],
                help_text="Select the topics that this page relates to.",
                heading="Taxonomy",
            ),
            ObjectList(BasePage.promote_panels, heading="Promote"),
        ]
    )

    def clean(self):
        super().clean()
        if TopicPage.objects.filter(topic=self.topic).exists():
            raise ValidationError({"topic": "Topic Page with this topic already exists."})

