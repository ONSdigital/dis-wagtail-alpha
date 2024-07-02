from ons_alpha.core.models.base import BasePage
from ons_alpha.core.models.mixins import SubpageMixin


class TopicPage(SubpageMixin, BasePage):
    template = "templates/pages/topics/topic_page.html"
    parent_page_types = ["topics.TopicSectionPage"]


class TopicSectionPage(SubpageMixin, BasePage):
    template = "templates/pages/topics/topic_section_page.html"
    subpage_types = ["topics.TopicSectionPage", "topics.TopicPage"]
