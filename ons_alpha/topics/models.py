from ons_alpha.core.models.base import BasePage
from ons_alpha.core.models.mixins import SubpageMixin


class TopicPage(SubpageMixin, BasePage):
    template = "templates/pages/topics/topic_page.html"
    parent_page_types = ["topics.TopicSectionPage"]
    subpage_types = ["bulletins.BulletinSeriesPage"]
    page_description = "A specific topic page. e.g.  Public sector finance or  Inflation and price indices"


class TopicSectionPage(SubpageMixin, BasePage):
    template = "templates/pages/topics/topic_section_page.html"
    subpage_types = ["topics.TopicSectionPage", "topics.TopicPage"]
    page_description = "General topic page. e.g. Economy"
