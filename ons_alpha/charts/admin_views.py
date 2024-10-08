from django.db.models import FileField
from django.urls import path, reverse
from django.views.generic.edit import BaseFormView
from wagtail.admin.views.generic.base import WagtailAdminTemplateMixin
from wagtail.admin.views.generic.mixins import LocaleMixin
from wagtail.admin.views.generic.permissions import PermissionCheckedMixin
from wagtail.snippets.views.snippets import (
    CopyView,
    CreateView,
    DeleteView,
    EditView,
    HistoryView,
    PreviewOnCreateView,
    PreviewOnEditView,
    SnippetViewSet,
)

from .admin_forms import ChartTypeSelectForm
from .models import Chart
from .utils import get_chart_type_model_from_name


class ChartTypeSelectView(
    LocaleMixin, PermissionCheckedMixin, WagtailAdminTemplateMixin, BaseFormView
):
    def get_form_class(self):
        """Return the form class to use."""
        return ChartTypeSelectForm

    def get_template_names(self):
        return ["charts/admin/chart_type_select.html"]

    def form_valid(self, form):
        """Process the valid form data."""
        self.form = form  # Store the form instance
        return super().form_valid(form)

    def get_success_url(self):
        """Return the URL to redirect to after processing a valid form."""
        chart_type = self.form.cleaned_data["chart_type"]
        return reverse(
            "wagtailsnippets_charts_chart:specific_add",
            kwargs={"chart_type": chart_type},
        )


class ChartTypeKwargMixin:
    def setup(self, request, *args, **kwargs):
        self.model = get_chart_type_model_from_name(kwargs["chart_type"])
        super().setup(request, *args, **kwargs)

    def get_panel(self):
        edit_handler = self.model.edit_handler
        return edit_handler.bind_to_model(self.model)


class SpecificObjectViewMixin:
    draftstate_enabled = True
    locking_enabled = False
    preview_enabled = True
    revision_enabled = True

    def setup(self, request, *args, **kwargs):
        # NOTE: These 3 attributes will be reset by the superclass implementation,
        # but need to be set for the `get_object()` method to work
        # correctly
        self.request = request
        self.args = args
        self.kwargs = kwargs

        # Fetch the specific object and use the specific type to set
        # self.model - allowing forms to be generated correctly. Our overrides
        # to `get_object()` should rule out repeat queries when the superclass
        # implementation calls `get_object()` again.
        self.object = self.get_object()
        self.model = type(self.object)

        super().setup(request, *args, **kwargs)

    def get_object(self):
        """
        Overrides the default implementation to return the specific object.
        Because views often make their own requests to `get_object()` in
        `setup()`, there is some caching in place to avoid repeat queries.
        """
        if getattr(self, "object", None):
            return self.object.specific
        return super().get_object().specific

    def get_panel(self):
        edit_handler = self.model.edit_handler
        return edit_handler.bind_to_model(self.model)


class SpecificAddView(ChartTypeKwargMixin, CreateView):
    def get_add_url(self):
        # This override is required so that the form posts back to this view
        return reverse(
            "wagtailsnippets_charts_chart:specific_add",
            kwargs={"chart_type": self.kwargs["chart_type"]},
        )

    def get_preview_url(self):
        """
        Overrides the default implementation to pass include the chart-type
        in the preview URL, allowing it to identify the specific model.
        """
        args = [self.model._meta.label_lower]
        return reverse(self.preview_url_name, args=args)


class SpecificEditView(SpecificObjectViewMixin, EditView):
    action = "edit"

    def get_preview_url(self):
        """
        Overrides the default implementation to pass include the chart-type
        in the preview URL, allowing it to identify the specific model.
        """
        args = [self.model._meta.label_lower, self.object.pk]
        return reverse(self.preview_url_name, args=args)


class SpecificCopyView(SpecificObjectViewMixin, CopyView):
    action = "copy"

    def get_initial_form_instance(self):
        """
        Overrides the default implementation to ensure file field values
        are set to None, so that the editor is forced to upload new files.
        """
        instance = super().get_initial_form_instance()
        for field in self.model._meta.get_fields():
            if isinstance(field, FileField):
                setattr(instance, field.name, None)
        return instance

    def get_add_url(self):
        """
        Overrides the default implementation to ensure the form is posted
        to the 'specific_add' view - which has a chart-type-specific form
        for validating/saving the new object.
        """
        return reverse(
            "wagtailsnippets_charts_chart:specific_add",
            kwargs={"chart_type": self.model._meta.label_lower},
        )

    def get_preview_url(self):
        """
        Overrides the default implementation to include the chart-type
        in the preview URL, allowing it to identify the specific model.
        """
        args = [self.model._meta.label_lower]
        return reverse(self.preview_url_name, args=args)


class SpecificDeleteView(SpecificObjectViewMixin, DeleteView):
    def get_form(self, *args, **kwargs):
        """
        Overrides the default implementation to ensure 'instance' is set on
        the form. It's unclear why Wagtail doesn't do this by default, but
        `self.get_bound_panel()` raises an AttributeError without this.
        """
        form = super().get_form(*args, **kwargs)
        form.instance = self.object
        return form


class SpecificPreviewOnCreateView(ChartTypeKwargMixin, PreviewOnCreateView):
    pass


class SpecificPreviewOnEditView(ChartTypeKwargMixin, PreviewOnEditView):
    pass


class SpecificHistoryView(SpecificObjectViewMixin, HistoryView):
    pass


class ChartViewSet(SnippetViewSet):
    add_to_admin_menu = True
    add_view_class = ChartTypeSelectView
    copy_view_class = SpecificCopyView
    delete_view_class = SpecificDeleteView
    edit_view_class = SpecificEditView
    history_view_class = SpecificHistoryView
    model = Chart
    preview_on_add_view_class = SpecificPreviewOnCreateView
    preview_on_edit_view_class = SpecificPreviewOnEditView
    specific_add_view_class = SpecificAddView

    @property
    def specific_add_view(self):
        return self.construct_view(
            self.specific_add_view_class, **self.get_add_view_kwargs()
        )

    def get_urlpatterns(self):
        urlpatterns = [
            pattern
            for pattern in super().get_urlpatterns()
            if getattr(pattern, "name", "") not in ["preview_on_add", "preview_on_edit"]
        ]
        urlpatterns.extend(
            [
                path(
                    "new/<str:chart_type>/", self.specific_add_view, name="specific_add"
                ),
                path(
                    "preview/<str:chart_type>/",
                    self.preview_on_add_view,
                    name="preview_on_add",
                ),
                path(
                    "preview/<str:chart_type>/<str:pk>/",
                    self.preview_on_edit_view,
                    name="preview_on_edit",
                ),
            ]
        )
        return urlpatterns

    def get_add_view_kwargs(self, **kwargs):
        kwargs = super().get_add_view_kwargs(**kwargs)
        del kwargs["panel"]
        del kwargs["form_class"]
        return kwargs

    def get_edit_view_kwargs(self, **kwargs):
        kwargs = super().get_edit_view_kwargs(**kwargs)
        del kwargs["panel"]
        del kwargs["form_class"]
        return kwargs

    @property
    def preview_on_add_view(self):
        return self.construct_view(self.preview_on_add_view_class)

    @property
    def preview_on_edit_view(self):
        return self.construct_view(self.preview_on_edit_view_class)
