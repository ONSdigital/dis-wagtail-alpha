from django import forms
from django.utils.translation import gettext_lazy as _
from tbxforms.choices import Choice
from tbxforms.fields import DateInputField
from tbxforms.layout import HTML, Button, Field, Fieldset, Layout

from ons_alpha.utils.forms import BaseFormMixin


class ExampleForm(BaseFormMixin, forms.Form):
    """Demonstration of some common fields / widgets."""

    RADIO_AND_CHECKBOX_CHOICES = (
        Choice(
            value="one",
            label="Option one",
            hint="Optional hint text",
        ),
        Choice(
            value="two",
            label="Option two",
        ),
        Choice(
            value="three",
            label="Option three",
            hint="Another optional hint text",
        ),
        Choice(
            value="four",
            label="Option four",
        ),
    )
    SELECT_CHOICES = (
        Choice(
            value="",
            label="Please select…",
        ),
        *RADIO_AND_CHECKBOX_CHOICES,
    )

    single_line_text = forms.CharField(
        max_length=255,
        help_text="This is some help text",
    )
    single_line_text_optional = forms.CharField(
        required=False,
    )
    single_line_text_disabled = forms.CharField(
        disabled=True,
    )
    multi_line_text = forms.CharField(
        widget=forms.Textarea(),
    )
    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={"autocomplete": "email", "autocapitalize": "off"}
        ),
    )
    number = forms.IntegerField(
        widget=forms.NumberInput(attrs={"step": 1}),
    )
    url = forms.URLField(
        label="URL",
    )
    date = DateInputField(
        require_all_fields=False,
    )
    time = forms.TimeField(
        widget=forms.TextInput(attrs={"type": "time"}),
    )
    datetime = forms.DateTimeField(
        widget=forms.TextInput(attrs={"type": "datetime-local"}),
    )
    file = forms.FileField(
        help_text="Please upload a CSV or XLS",
    )
    password = forms.CharField(
        widget=forms.PasswordInput(),
    )
    hidden = forms.CharField(
        widget=forms.HiddenInput(),
    )
    single_checkbox = forms.BooleanField()
    multiple_checkboxes = forms.MultipleChoiceField(
        choices=RADIO_AND_CHECKBOX_CHOICES,
        widget=forms.CheckboxSelectMultiple(),
    )
    multiple_checkboxes_one = forms.CharField(
        max_length=255,
        required=False,
    )
    select = forms.ChoiceField(
        choices=SELECT_CHOICES,
    )
    radio_buttons = forms.ChoiceField(
        choices=RADIO_AND_CHECKBOX_CHOICES,
        widget=forms.RadioSelect(),
    )
    radio_buttons_three_or_four = forms.CharField(
        max_length=255,
        required=False,
    )
    fs_single_line_text_1 = forms.CharField(
        max_length=255,
    )
    fs_single_line_text_2 = forms.CharField(
        max_length=255,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper.layout = Layout(
            # ----------------------------------------------------------------
            # Add the fields we're not manipulating.
            Field.text("single_line_text"),
            Field.text("single_line_text_optional"),
            Field.text("single_line_text_disabled"),
            Field.textarea("multi_line_text"),
            Field.text("email"),
            Field.text("url"),
            Field.text("date"),
            Field.text("time"),
            Field.text("datetime"),
            Field.text("file"),
            Field.text("password"),
            Field.text("hidden"),
            Field.select("select"),
            Field.checkbox("single_checkbox"),
            Field.checkboxes("multiple_checkboxes"),
            Field.radios("radio_buttons"),
            Field.text("number"),
            # ----------------------------------------------------------------
            # Conditional field for checkboxes.
            HTML(
                """
                <p>Hint: To see the conditional field below, select option
                `one` in the above checkbox field.</p>
                """
            ),
            Field.checkboxes(
                "multiple_checkboxes_one",
                data_conditional={
                    "field_name": "multiple_checkboxes",
                    "values": ["one"],
                },
            ),
            # ----------------------------------------------------------------
            # Conditional field for radios.
            HTML(
                """
                <p>Hint: To see the conditional field below, choose option
                `three` or `four` in the above radio button field.</p>
                """
            ),
            Field.radios(
                "radio_buttons_three_or_four",
                data_conditional={
                    "field_name": "radio_buttons",
                    "values": ["three", "four"],
                },
            ),
            # ----------------------------------------------------------------
            # Group some fields within a fieldset
            Fieldset(
                Field.text("fs_single_line_text_1"),
                Field.text("fs_single_line_text_2"),
                legend="Fieldset title",
            ),
            # ----------------------------------------------------------------
            # Add a submit button
            Button.primary(
                name="submit",
                type="submit",
                value=_("Submit"),
                css_class="form__submit",
            ),
        )

    @staticmethod
    def conditional_fields_to_show_as_required() -> list[str]:
        return [
            "multiple_checkboxes_one",
            "radio_buttons_three_or_four",
        ]
