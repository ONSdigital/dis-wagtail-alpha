# Create TopicViewSet
from wagtail.admin.viewsets.chooser import ChooserViewSet
from wagtail.admin.viewsets.model import ModelViewSet

from .models import Topic


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


topic_viewset = TopicViewSet("topics")
topic_chooser_viewset = TopicChooserViewSet("topic_chooser")
