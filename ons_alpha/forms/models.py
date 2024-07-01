from django.db import models
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from modelcluster.fields import ParentalKey
from wagtail.admin.panels import FieldPanel, FieldRowPanel, InlinePanel, MultiFieldPanel
from wagtail.contrib.forms.models import AbstractEmailForm, AbstractFormField
from wagtail.fields import RichTextField
from wagtail.search import index

from ons_alpha.core.models import BasePage
from ons_alpha.utils.forms import WagtailFormBuilder


class FormField(AbstractFormField):
    page = ParentalKey("FormPage", related_name="form_fields")


# Never cache form pages since they include CSRF tokens.
@method_decorator(never_cache, name="serve")
class FormPage(AbstractEmailForm, BasePage):
    template = "templates/pages/forms/form_page.html"
    landing_page_template = "templates/pages/forms/form_page_landing.html"

    form_builder = WagtailFormBuilder
    search_fields = BasePage.search_fields + [index.SearchField("introduction")]
    subpage_types = []

    introduction = models.TextField(blank=True)
    thank_you_text = RichTextField(
        blank=True,
        help_text="Text displayed to the user on successful submission of the form",
    )
    action_text = models.CharField(
        max_length=32,
        blank=True,
        help_text='Form action text. Defaults to "Submit"',
    )

    def get_form_parameters(self):
        """Pass our 'action_text' to the `form_builder`."""
        return {"action_text": self.action_text}

    content_panels = BasePage.content_panels + [
        FieldPanel("introduction"),
        InlinePanel("form_fields", label="Form fields"),
        FieldPanel("action_text"),
        FieldPanel("thank_you_text"),
        MultiFieldPanel(
            [
                FieldRowPanel(
                    [
                        FieldPanel("from_address", classname="col6"),
                        FieldPanel("to_address", classname="col6"),
                    ]
                ),
                FieldPanel("subject"),
            ],
            "Email",
        ),
    ]
