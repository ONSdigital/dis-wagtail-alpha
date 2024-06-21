from django.utils.translation import gettext_lazy as _

from wagtail.contrib.forms.forms import BaseForm as WagtailBaseForm

from tbxforms import forms as tbxforms_forms
from tbxforms.layout import Button
from wagtailcaptcha.forms import WagtailCaptchaFormBuilder


class BaseFormMixin(tbxforms_forms.TbxFormsMixin):
    """
    A base class that should be used/inherited by all forms.
    Outputs a standard form with the <form> tag.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper.form_error_title = _("There is a problem with your submission")


class BaseWagtailForm(BaseFormMixin, WagtailBaseForm):
    """
    For forms built by `wagtail.contrib.forms` where we want to utilise our
    FormPage.action_text as the submit button text.
    """

    def __init__(self, *args, **kwargs):
        self.action_text = kwargs.pop("action_text", None)
        super().__init__(*args, **kwargs)
        self.helper.layout.extend(
            [
                Button.primary(
                    name="submit",
                    type="submit",
                    value=self.action_text or _("Submit"),
                    css_class="form__submit",
                )
            ]
        )


class WagtailFormBuilder(
    WagtailCaptchaFormBuilder, tbxforms_forms.BaseWagtailFormBuilder
):
    """
    Instructs a Page model to use our `BaseWagtailForm` form variant, as well
    as inheriting some field/widget definitions from `BaseWagtailFormBuilder`.

    Usage: Add `form_builder = WagtailFormBuilder` to your form page model.
    """

    def get_form_class(self):
        return type("WagtailForm", (BaseWagtailForm,), self.formfields)
