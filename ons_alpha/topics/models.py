from django.core.exceptions import ValidationError
from django.db import models
from wagtail.admin.panels import FieldPanel, ObjectList, TabbedInterface

from ons_alpha.core.models.base import BasePage
from ons_alpha.core.models.mixins import SubpageMixin
from ons_alpha.taxonomy.models import Topic
from ons_alpha.taxonomy.views import topic_page_topic_chooser_viewset, topic_section_page_topic_chooser_viewset


class TopicPage(SubpageMixin, BasePage):
    _taxonomy_widget_class = topic_page_topic_chooser_viewset.widget_class

    template = "templates/pages/topics/topic_page.html"
    parent_page_types = ["topics.TopicSectionPage"]
    subpage_types = ["bulletins.BulletinSeriesPage"]
    page_description = "A specific topic page. e.g. Public sector finance or Inflation and price indices"

    topic = models.OneToOneField(
        Topic,
        on_delete=models.SET_NULL,
        null=True,
        blank=False,
        related_name="topic_page",
    )

    content_panels = BasePage.content_panels

    edit_handler = TabbedInterface(
        [
            ObjectList(content_panels, heading="Content"),
            ObjectList(
                [FieldPanel("topic", widget=_taxonomy_widget_class)],
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


class TopicSectionPage(SubpageMixin, BasePage):
    _taxonomy_widget_class = topic_section_page_topic_chooser_viewset.widget_class

    template = "templates/pages/topics/topic_section_page.html"
    subpage_types = ["topics.TopicSectionPage", "topics.TopicPage"]
    page_description = "General topic page. e.g. Economy"

    topic = models.OneToOneField(
        Topic,
        on_delete=models.SET_NULL,
        null=True,
        blank=False,
        related_name="topic_section_page",
    )

    content_panels = BasePage.content_panels

    edit_handler = TabbedInterface(
        [
            ObjectList(content_panels, heading="Content"),
            ObjectList(
                [FieldPanel("topic", widget=_taxonomy_widget_class)],
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
