from django import template

from ons_alpha.core.models import SocialMediaSettings


register = template.Library()


# Social text
@register.filter(name="social_text")
def social_text(page, site):
    return getattr(page, "social_text", None) or SocialMediaSettings.for_site(site).default_sharing_text


# Social image
@register.filter(name="social_image")
def social_image(page, site):
    return getattr(page, "social_image", None) or SocialMediaSettings.for_site(site).default_sharing_image
