from functools import cached_property

from wagtail.admin.ui.tables import Column, UpdatedAtColumn, UserColumn
from wagtail.admin.views.generic import CreateView, IndexView
from wagtail.admin.views.generic.chooser import ChooseView
from wagtail.admin.viewsets.chooser import ChooserViewSet
from wagtail.admin.viewsets.model import ModelViewSet

from .models import Bundle


class BundleCrateView(CreateView):
    def save_instance(self):
        instance = super().save_instance()
        instance.created_by = self.request.user
        instance.save(update_fields=["created_by"])
        return instance


class BundleIndexView(IndexView):
    def get_queryset(self):
        queryset = super().get_queryset()

        return queryset.select_related("topic", "created_by")

    @cached_property
    def columns(self):
        return [
            self._get_title_column("__str__"),
            Column("topic"),
            Column("scheduled_publication_date"),
            Column("get_status_display", label="Status"),
            UpdatedAtColumn(),
            UserColumn("created_by"),
        ]


class BundleChooseView(ChooseView):
    icon = "boxes-stacked"

    @property
    def columns(self):
        return super().columns + [
            Column("topic", label="Topic", accessor="topic.title"),
            Column("scheduled_publication_date"),
            UserColumn("created_by"),
        ]

    def get_object_list(self):
        return Bundle.objects.select_related("topic", "created_by").only("name", "created_by", "topic__title")


class BundleChooserViewSet(ChooserViewSet):
    model = Bundle
    icon = "boxes-stacked"
    choose_view_class = BundleChooseView
    preserve_url_parameters = ["multiple", "topic"]
    url_filter_parameters = ["topic"]

    def get_object_list(self):
        return self.model.editable_objects.all()


class BundleViewSet(ModelViewSet):
    model = Bundle
    icon = "boxes-stacked"
    add_view_class = BundleCrateView
    index_view_class = BundleIndexView
    chooser_viewset_class = BundleChooserViewSet
    list_filter = ["status", "created_by"]
    add_to_admin_menu = True
    inspect_view_enabled = True


bundle_viewset = BundleViewSet("bundle")
bundle_chooser_viewset = BundleChooserViewSet("bundle_chooser")

BundleChooserWidget = bundle_chooser_viewset.widget_class
