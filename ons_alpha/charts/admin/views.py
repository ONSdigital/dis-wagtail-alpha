from django.urls import path, reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic.edit import BaseFormView
from wagtail.admin.ui.components import MediaContainer
from wagtail.admin.ui.side_panels import ChecksSidePanel
from wagtail.admin.ui.tables import LiveStatusTagColumn
from wagtail.admin.views.generic.base import WagtailAdminTemplateMixin
from wagtail.admin.views.generic.mixins import LocaleMixin
from wagtail.admin.views.generic.permissions import PermissionCheckedMixin
from wagtail.log_actions import log
from wagtail.snippets.action_menu import DeleteMenuItem, PublishMenuItem, UnpublishMenuItem
from wagtail.snippets.views.snippets import (
    CreateView,
    DeleteView,
    EditView,
    HistoryView,
    PreviewOnCreateView,
    PreviewOnEditView,
    SnippetViewSet,
)

from ons_alpha.charts.admin.filters import ChartFilterSet
from ons_alpha.charts.admin.forms import ChartCopyForm, ChartTypeSelectForm
from ons_alpha.charts.models import Chart
from ons_alpha.charts.utils import get_chart_type_model_from_name


class ChartTypeSelectView(LocaleMixin, PermissionCheckedMixin, WagtailAdminTemplateMixin, BaseFormView):
    def get_form_class(self):
        """Return the form class to use."""
        return ChartTypeSelectForm

    def get_template_names(self):
        return ["charts/admin/chart_type_select.html"]

    def form_valid(self, form):
        """Process the valid form data."""
        self.form = form  # pylint: disable=attribute-defined-outside-init
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

    def get_object(self, queryset=None):
        """
        Overrides the default implementation to return the specific object.
        Because views often make their own requests to `get_object()` in
        `setup()`, there is some caching in place to avoid repeat queries.
        """
        if getattr(self, "object", None):
            return self.object.specific
        return super().get_object(queryset).specific

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

    def get_side_panels(self):
        return MediaContainer([panel for panel in super().get_side_panels() if not isinstance(panel, ChecksSidePanel)])


class SpecificEditView(SpecificObjectViewMixin, EditView):
    action = "edit"

    def get_preview_url(self):
        """
        Overrides the default implementation to pass include the chart-type
        in the preview URL, allowing it to identify the specific model.
        """
        args = [self.model._meta.label_lower, self.object.pk]
        return reverse(self.preview_url_name, args=args)

    def get_side_panels(self):
        return MediaContainer([panel for panel in super().get_side_panels() if not isinstance(panel, ChecksSidePanel)])


class ChartCopyView(SpecificObjectViewMixin, EditView):
    action = "copy"
    permission_required = "add"
    success_message = _("%(model_name)s '%(object)s' created successfully.")

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.revision_enabled = False
        self.locking_enabled = False

    def get_header_title(self):
        return f"Copy chart: {self.object}"

    def get_page_subtitle(self):
        return f"Copy: {self.object}"

    def get_form(self, *args, **kwargs):  # pylint: disable=unused-argument
        form = ChartCopyForm(
            data=self.request.POST or None, instance=self.object, initial={"name": self.object.name + " copy"}
        )
        return form

    def run_before_hook(self):
        return self.run_hook("before_create_snippet", self.request, self.object)

    def run_after_hook(self):
        return self.run_hook("after_create_snippet", self.request, self.object)

    def get_side_panels(self):
        return MediaContainer()

    def _get_action_menu(self):
        menu = super()._get_action_menu()
        menu.menu_items = [
            item
            for item in menu.menu_items
            if not isinstance(item, (DeleteMenuItem, PublishMenuItem, UnpublishMenuItem))
        ]
        return menu

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["action_url"] = self.request.path
        return context

    def save_instance(self):
        """
        Called after the form is successfully validated - saves the object to the db
        and returns the new object. Override this to implement custom save logic.
        """
        instance = self.form.save()
        instance.save_revision(user=self.request.user)

        log(
            instance=instance,
            action="wagtail.create",
            revision=None,
            content_changed=False,
        )

        return instance

    def get_success_url(self):
        return reverse(self.index_url_name)


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
    copy_view_class = ChartCopyView
    delete_view_class = SpecificDeleteView
    edit_view_class = SpecificEditView
    history_view_class = SpecificHistoryView
    model = Chart
    preview_on_add_view_class = SpecificPreviewOnCreateView
    preview_on_edit_view_class = SpecificPreviewOnEditView
    specific_add_view_class = SpecificAddView
    filterset_class = ChartFilterSet
    list_display = ["name", LiveStatusTagColumn(), "chart_type", "first_published_at", "last_published_at"]

    @property
    def specific_add_view(self):
        return self.construct_view(self.specific_add_view_class, **self.get_add_view_kwargs())

    def get_urlpatterns(self):
        urlpatterns = [
            pattern
            for pattern in super().get_urlpatterns()
            if getattr(pattern, "name", "") not in ["preview_on_add", "preview_on_edit"]
        ]
        urlpatterns.extend(
            [
                path("new/<str:chart_type>/", self.specific_add_view, name="specific_add"),
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
