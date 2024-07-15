from wagtail import hooks

from ons_alpha.taxonomy.views import (
    default_topic_chooser_viewset,
    topic_page_topic_chooser_viewset,
    topic_section_page_topic_chooser_viewset,
    topic_viewset,
)


@hooks.register("register_admin_viewset")
def register_topic_viewset():
    return topic_viewset


@hooks.register("register_admin_viewset")
def register_topic_page_topic_chooser_viewset():
    return topic_page_topic_chooser_viewset


@hooks.register("register_admin_viewset")
def register_topic_section_page_topic_chooser_viewset():
    return topic_section_page_topic_chooser_viewset


@hooks.register("register_admin_viewset")
def register_topic_chooser_viewset():
    return default_topic_chooser_viewset
