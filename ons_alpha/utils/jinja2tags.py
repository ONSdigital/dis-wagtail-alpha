from crispy_forms.utils import render_crispy_form
from django.templatetags.static import static
from jinja2 import pass_context
from jinja2.ext import Extension
from wagtail.contrib.routable_page.templatetags.wagtailroutablepage_tags import routablepageurl
from wagtail.models import Locale
from wagtailmath.templatetags.wagtailmath import mathjax

from ons_alpha.navigation.templatetags.navigation_tags import footer_nav, primary_nav, secondary_nav
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
                "static": static,
                "routablepageurl": pass_context(routablepageurl),
                "translation_urls": get_translation_urls,
            }
        )

        self.environment.filters.update(
            {
                "social_text": social_text,
                "social_image": social_image,
            }
        )


@pass_context
def get_translation_urls(context) -> list[dict[str, str | bool]]:
    if not (page := context.get("page")):
        return []

    default_locale = Locale.get_default()
    variants = {variant.locale_id: variant for variant in page.get_translations(inclusive=True)}
    default_page = variants.get(default_locale.pk)
    urls = []
    for locale in Locale.objects.all().order_by("pk"):
        variant = variants.get(locale.pk, default_page)
        url = variant.get_url(request=context["request"])
        if variant == default_page and locale.pk != variant.locale_id:
            # if there is no translation in this locale, append the language code to the path
            # Wagtail will serve the original page, but strings in templates will be localized
            url = f"/{locale.language_code}{url}"

        urls.append(
            {
                "url": url,
                "ISOCode": locale.language_code.split("-", 1)[0],
                "text": locale.language_name_local,
                "current": locale.is_active,
            }
        )

    return urls
