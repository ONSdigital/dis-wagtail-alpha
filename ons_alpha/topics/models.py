from django.core.exceptions import ValidationError
from django.db import models
from wagtail.admin.panels import FieldPanel, ObjectList, TabbedInterface

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
    summary = models.CharField(blank=True, max_length=255)
    topic_page_nav = models.CharField(blank=True, max_length=255)
    # a list of distinct page types for descendants and associated documents

    content_panels = BasePage.content_panels + [
        FieldPanel("summary"),
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

    def topic_list_child_page_types(self):
        """
        For a topic page will return a distinct list of child page types
        """
        list_items = self.get_children().live().public().specific()
        display_names = []
        for menu_item in list_items:
            display_names.append(menu_item.specific.page_type_display_name)
        return sorted(set(display_names))

    def topic_descendents_by_page_type  (self):
        child_page_types = self.topic_list_child_page_types()
        display_names = {}
        for child_page_type in child_page_types:
            display_names[child_page_type] = []
            subpage_list = []

            for subpage in self.get_children().live().public().specific():
                if subpage.specific.page_type_display_name == child_page_type:
                    if subpage.get_children().live().public().specific().exists():
                        for child_page in subpage.get_children().live().public().specific():
                            subpage_list.append(child_page)
                    else:
                        subpage_list.append(subpage)
                display_names[child_page_type] = subpage_list
        return display_names

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        context["topic_list"] = self.topic_list_child_page_types()
        context["subpage_dict"] = self.topic_descendents_by_page_type()
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
