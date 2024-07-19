from functools import cached_property

from wagtail.admin.ui.tables import Column, UpdatedAtColumn, UserColumn
from wagtail.admin.views.generic import CreateView, IndexView
from wagtail.admin.viewsets.model import ModelViewSet

from .models import Bundle


class BundleCrateView(CreateView):
    def save_instance(self):
        instance = super().save_instance()
        instance.created_by = self.request.user
        instance.save(update_fields=["created_by"])
        return instance


class BundleIndexView(IndexView):
    @cached_property
    def columns(self):
        return [
            self._get_title_column("__str__"),
            Column("scheduled_publication_date"),
            Column("get_status_display", label="Status"),
            UpdatedAtColumn(),
            UserColumn("created_by"),
        ]


class BundleViewSet(ModelViewSet):
    model = Bundle
    icon = "boxes-stacked"
    add_view_class = BundleCrateView
    index_view_class = BundleIndexView
    list_filter = ["status", "created_by"]
    add_to_admin_menu = True
    inspect_view_enabled = True


bundle_viewset = BundleViewSet("bundle")
