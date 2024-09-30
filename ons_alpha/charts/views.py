from django.http import Http404
from django.urls import path, reverse
from django.views.generic.edit import BaseFormView
from wagtail.admin.views.generic.base import WagtailAdminTemplateMixin
from wagtail.admin.views.generic.mixins import LocaleMixin
from wagtail.admin.views.generic.permissions import PermissionCheckedMixin
from wagtail.snippets.views.snippets import CreateView, DeleteView, EditView, SnippetViewSet

from .admin_forms import ChartTypeSelectForm
from .models import Chart
from .utils import get_chart_type_model_from_name


class ChartTypeSelectView(LocaleMixin, PermissionCheckedMixin, WagtailAdminTemplateMixin, BaseFormView):
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
        return reverse("wagtailsnippets_charts_chart:specific_add", kwargs={"chart_type": chart_type})


class SpecificAddView(CreateView):

    def setup(self, request, *args, **kwargs):
        try:
            self.model = get_chart_type_model_from_name(kwargs.get("chart_type"))
        except ValueError:
            raise Http404("Invalid chart type") from None

        # This override is required to cancel-out the `form_class`` added
        # by the SnippetViewSet, allowing the view to use `get_panel()`
        # to assemble one for the specific model
        self.form_class = None
        super().setup(request, *args, **kwargs)

    def get_add_url(self):
        # This override is required so that the form posts back to this view
        return reverse("wagtailsnippets_charts_chart:specific_add", kwargs={"chart_type": self.kwargs["chart_type"]})

    def get_panel(self):
        edit_handler = self.model.edit_handler
        return edit_handler.bind_to_model(self.model)


class SpecificEditView(EditView):

    def setup(self, request, *args, **kwargs):
        # This override is required to cancel out the 'form_class' added
        # by the SnippetViewSet, and allow a form to be generated from the
        # specific model instead
        self.form_class = None

        super().setup(request, *args, **kwargs)

        # Convert the vanilla Chart object into a specific one
        self.object = self.object.specific
        self.model = type(self.object)

    def get_panel(self):
        edit_handler = self.model.edit_handler
        return edit_handler.bind_to_model(self.model)


class SpecificDeleteView(DeleteView):

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.object = self.object.specific
        self.specific_model = type(self.object)


class ChartViewSet(SnippetViewSet):
    model = Chart
    add_view_class = ChartTypeSelectView
    specific_add_view_class = SpecificAddView
    edit_view_class = SpecificEditView
    delete_view_class = SpecificDeleteView

    @property
    def specific_add_view(self):
        return self.construct_view(self.specific_add_view_class, **self.get_add_view_kwargs())

    def get_urlpatterns(self):
        urlpatterns = super().get_urlpatterns()
        urlpatterns.append(
            path("new/<str:chart_type>/", self.specific_add_view, name="specific_add"),
        )
        return urlpatterns
