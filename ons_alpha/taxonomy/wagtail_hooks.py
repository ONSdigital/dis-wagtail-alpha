from wagtail import hooks

from ons_alpha.taxonomy.views import (
    topic_chooser_viewset,
    topic_viewset,
)


@hooks.register("register_admin_viewset")
def register_topic_viewset():
    return topic_viewset


@hooks.register("register_admin_viewset")
def register_topic_chooser_viewset():
    return topic_chooser_viewset
