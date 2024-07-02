from django.core.exceptions import ValidationError
from django.db import models
from wagtail.admin.panels import FieldPanel, MultiFieldPanel


class LinkFields(models.Model):
    """
    Adds fields for internal and external links with some methods to simplify the rendering:

    <a href="{{ obj.get_link_url }}">{{ obj.get_link_text }}</a>
    """

    link_page = models.ForeignKey("wagtailcore.Page", blank=True, null=True, on_delete=models.SET_NULL)
    link_url = models.URLField(blank=True)
    link_text = models.CharField(blank=True, max_length=255)

    class Meta:
        abstract = True

    def clean(self):
        if not self.link_page and not self.link_url:
            raise ValidationError(
                {
                    "link_url": ValidationError("You must specify link page or link url."),
                    "link_page": ValidationError("You must specify link page or link url."),
                }
            )

        if self.link_page and self.link_url:
            raise ValidationError(
                {
                    "link_url": ValidationError("You must specify link page or link url. You can't use both."),
                    "link_page": ValidationError("You must specify link page or link url. You can't use both."),
                }
            )

        if not self.link_page and not self.link_text:
            raise ValidationError(
                {"link_text": ValidationError("You must specify link text, if you use the link url field.")}
            )

    def get_link_text(self):
        if self.link_text:
            return self.link_text

        if self.link_page:
            return self.link_page.title

        return ""

    def get_link_url(self):
        if self.link_page:
            return self.link_page.get_url

        return self.link_url

    panels = [
        MultiFieldPanel(
            [
                FieldPanel("link_page"),
                FieldPanel("link_url"),
                FieldPanel("link_text"),
            ],
            "Link",
        )
    ]
