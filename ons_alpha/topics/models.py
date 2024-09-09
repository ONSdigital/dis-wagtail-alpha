from django.core.exceptions import ValidationError
from django.db import models
from wagtail.admin.panels import FieldPanel, ObjectList, TabbedInterface

from ons_alpha.core.models.base import BasePage
from ons_alpha.core.models.mixins import SubpageMixin
from ons_alpha.taxonomy.models import Topic


class BaseTopicPage(SubpageMixin, BasePage):
    summary = models.TextField(blank=True)

    topic = models.ForeignKey(
        Topic,
        on_delete=models.SET_NULL,
        null=True,
        blank=False,
        related_name="%(class)s",
        # '%(class)s' is replaced by the lowercased name of the child class that the field is used in.
        # https://docs.djangoproject.com/en/5.0/topics/db/models/#be-careful-with-related-name-and-related-query-name
    )

    content_panels = BasePage.content_panels + [FieldPanel("summary")]

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
    subpage_types = ["articles.ArticleSeriesPage", "bulletins.BulletinSeriesPage", "methodologies.MethodologyPage"]
    page_description = "A specific topic page. e.g. Public sector finance or Inflation and price indices"


class TopicSectionPage(BaseTopicPage):
    template = "templates/pages/topics/topic_section_page.html"
    subpage_types = ["topics.TopicSectionPage", "topics.TopicPage"]
    page_description = "General topic page. e.g. Economy"
