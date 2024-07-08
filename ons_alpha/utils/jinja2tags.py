from crispy_forms.utils import render_crispy_form
from jinja2 import pass_context
from jinja2.ext import Extension
from wagtailmath.templatetags.wagtailmath import mathjax

from ons_alpha.navigation.templatetags.navigation_tags import (
    footer_nav,
    primary_nav,
    secondary_nav,
)
from ons_alpha.utils.templatetags.util_tags import social_image, social_text


class UtilsExtension(Extension):  # pylint: disable=abstract-method
    def __init__(self, environment):
        super().__init__(environment)

        self.environment.globals.update(
            {
                "primary_nav": pass_context(primary_nav),
                "secondary_nav": pass_context(secondary_nav),
                "footer_nav": pass_context(footer_nav),
                "crispy": render_crispy_form,
                "mathjax": mathjax,
            }
        )

        self.environment.filters.update(
            {
                "social_text": social_text,
                "social_image": social_image,
            }
        )
