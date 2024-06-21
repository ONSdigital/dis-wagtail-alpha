from pattern_library.monkey_utils import override_tag

from ons_alpha.navigation.templatetags.navigation_tags import register


override_tag(register, name="primary_nav", default_html="")
override_tag(register, name="secondary_nav", default_html="")
override_tag(register, name="footer_nav", default_html="")
override_tag(register, name="sidebar", default_html="")
override_tag(register, name="footer_links", default_html="")
