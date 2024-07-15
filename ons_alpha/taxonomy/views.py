# Create TopicViewSet
from wagtail.admin.views.generic.chooser import ChooseResultsView, ChooseView
from wagtail.admin.viewsets.chooser import ChooserViewSet
from wagtail.admin.viewsets.model import ModelViewSet

from .models import Topic


class TopicChooserMixin:
    def get_object_list(self):
        # Only show top-level topics
        return Topic.get_root_nodes()


class SubTopicChooserMixin:
    def get_object_list(self):
        # Only show topic that have a parent
        return Topic.objects.exclude(depth=1).order_by("path")


class TopicChooseView(TopicChooserMixin, ChooseView): ...


class TopicChooseResultsView(TopicChooserMixin, ChooseResultsView): ...


class SubTopicChooseView(SubTopicChooserMixin, ChooseView): ...


class SubTopicChooseResultsView(SubTopicChooserMixin, ChooseResultsView): ...


class TopicViewSet(ModelViewSet):
    model = Topic
    icon = "tag"
    add_to_admin_menu = True
    menu_order = 200


class TopicChooserViewSet(ChooserViewSet):
    model = Topic

    icon = "tag"
    choose_one_text = "Choose a topic"
    choose_another_text = "Choose another topic"
    url_filter_parameters = ["country"]
    preserve_url_parameters = ["multiple", "country"]


class TopicPageTopicChooserViewSet(TopicChooserViewSet):
    choose_view_class = TopicChooseView
    choose_results_view_class = TopicChooseResultsView


class SubTopicPageTopicChooserViewSet(TopicChooserViewSet):
    choose_view_class = SubTopicChooseView
    choose_results_view_class = SubTopicChooseResultsView


topic_viewset = TopicViewSet("topics")
default_topic_chooser_viewset = TopicChooserViewSet("topic_chooser")
topic_page_topic_chooser_viewset = SubTopicPageTopicChooserViewSet("topic_page_topic_chooser")
topic_section_page_topic_chooser_viewset = TopicPageTopicChooserViewSet("topic_section_page_topic_chooser")
