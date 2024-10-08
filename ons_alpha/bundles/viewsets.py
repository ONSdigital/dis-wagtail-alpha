import time

from functools import cached_property

from django.http import HttpRequest
from django.shortcuts import redirect
from django.urls import reverse
from django.utils import timezone
from django.utils.html import format_html, format_html_join
from django.utils.translation import gettext as _
from wagtail.admin.ui.tables import Column, DateColumn, UpdatedAtColumn, UserColumn
from wagtail.admin.views.generic import CreateView, EditView, IndexView, InspectView
from wagtail.admin.views.generic.chooser import ChooseView
from wagtail.admin.viewsets.chooser import ChooserViewSet
from wagtail.admin.viewsets.model import ModelViewSet
from wagtail.log_actions import log

from .enums import BundleStatus
from .models import Bundle
from .notifications import notify_slack_of_publication_start, notify_slack_of_publish_end, notify_slack_of_status_change


class BundleCreateView(CreateView):
    def save_instance(self):
        # automatically set the creator
        instance = super().save_instance()
        instance.created_by = self.request.user
        instance.save(update_fields=["created_by"])
        return instance


class BundleEditView(EditView):
    actions = ["edit", "save-and-approve", "publish"]
    template_name = "bundles/wagtailadmin/edit.html"
    has_content_changes: bool = False
    start_time: float = None

    def dispatch(self, request: HttpRequest, *args, **kwargs):
        if (instance := self.get_object()) and instance.status == BundleStatus.RELEASED:
            return redirect(self.index_url_name)

        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if self.request.method == "POST":
            data = self.request.POST.copy()
            if "action-save-and-approve" in self.request.POST:
                data["status"] = BundleStatus.APPROVED.value
                data["approved_at"] = timezone.now()
                data["approved_by"] = self.request.user
                kwargs["data"] = data
            elif "action-publish" in self.request.POST:
                data["status"] = BundleStatus.RELEASED.value
                kwargs["data"] = data
        return kwargs

    def save_instance(self):
        instance = self.form.save()
        self.has_content_changes = self.form.has_changed()

        if self.has_content_changes:
            log(action="wagtail.edit", instance=instance, content_changed=True, data={"fields": self.form.changed_data})

            if "status" in self.form.changed_data:
                kwargs = {"content_changed": self.has_content_changes}
                original_status = BundleStatus[self.form.original_status].label
                url = self.request.build_absolute_uri(reverse("bundle:inspect", args=(instance.pk,)))

                if instance.status == BundleStatus.APPROVED.value:
                    action = "bundles.approve"
                    kwargs["data"] = {"old": original_status}
                    notify_slack_of_status_change(instance, original_status, user=self.request.user, url=url)
                elif instance.status == BundleStatus.RELEASED.value:
                    action = "wagtail.publish"
                    self.start_time = time.time()
                else:
                    action = "bundles.update_status"
                    kwargs["data"] = {
                        "old": original_status,
                        "new": instance.get_status_display(),
                    }
                    notify_slack_of_status_change(instance, original_status, user=self.request.user, url=url)

                # now log the status change
                log(
                    action=action,
                    instance=instance,
                    **kwargs,
                )

        return instance

    def run_after_hook(self):
        if self.action == "publish" or (self.action == "edit" and self.object.status == BundleStatus.RELEASED):
            notify_slack_of_publication_start(self.object, user=self.request.user)
            start_time = self.start_time or time.time()
            for page in self.object.get_bundled_pages():
                if page.current_workflow_state:
                    page.current_workflow_state.current_task_state.approve(user=self.request.user)

            notify_slack_of_publish_end(self.object, time.time() - start_time, user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # show the "save and approve" button if the bundle has the right status and we have a different user
        # than the creator
        context["show_save_and_approve"] = (
            self.object.can_be_approved and self.form.for_user.pk != self.object.created_by_id
        )
        context["show_publish"] = (
            self.object.status == BundleStatus.APPROVED and not self.object.scheduled_publication_date
        )

        return context


class BundleInspectView(InspectView):
    object: Bundle = None  # purely for typing purposes
    template_name = "bundles/wagtailadmin/inspect.html"

    def get_fields(self):
        return ["name", "status", "created_at", "created_by", "approved", "scheduled_publication", "pages", "datasets"]

    def get_field_label(self, field_name, field):
        match field_name:
            case "approved":
                return _("Approval status")
            case "scheduled_publication":
                return _("Scheduled publication")
            case "pages":
                return _("Pages")
            case _:
                return super().get_field_label(field_name, field)

    def get_field_display_value(self, field_name, field):
        # allow customising field display in the inspect class
        value_func = getattr(self, f"get_{field_name}_display_value", None)
        if value_func is not None:
            return value_func()

        return super().get_field_display_value(field_name, field)

    def get_approved_display_value(self):
        if self.object.status in [BundleStatus.APPROVED, BundleStatus.RELEASED]:
            if self.object.approved_by_id and self.object.approved_at:
                return f"{self.object.approved_by} on {self.object.approved_at}"
            return "Unknown approval data"
        return _("Pending approval")

    def get_scheduled_publication_display_value(self):
        return self.object.scheduled_publication_date or _("No scheduled publication")

    def get_pages_display_value(self):
        pages = self.object.get_bundled_pages().specific()
        data = (
            (
                reverse("wagtailadmin_pages:edit", args=(page.pk,)),
                page.get_admin_display_title(),
                page.get_verbose_name(),
                (
                    page.current_workflow_state.current_task_state.task.name
                    if page.current_workflow_state
                    else "not in a workflow"
                ),
                reverse("wagtailadmin_pages:view_draft", args=(page.pk,)),
            )
            for page in pages
        )

        page_data = format_html_join(
            "\n",
            '<tr><td class="title"><strong><a href="{}">{}</a></strong></td><td>{}</td><td>{}</td> '
            '<td><a href="{}" class="button button-small button-secondary">Preview</a></td></tr>',
            data,
        )

        return format_html(
            "<table class='listing'><thead><tr><th>Title</th><th>Type</th>"
            "<th>Status</th><th>Actions</th></tr></thead>{}</table>",
            page_data,
        )

    def get_datasets_display_value(self):
        content = [str(block) for block in self.object.datasets]
        return format_html("\n".join(content))


class BundleIndexView(IndexView):
    def get_queryset(self):
        queryset = super().get_queryset()

        return queryset.select_related("created_by")

    def get_edit_url(self, instance):
        # disable the edit URL for released bundles
        if instance.status != BundleStatus.RELEASED:
            return super().get_edit_url(instance)
        return None

    def get_copy_url(self, instance):
        # disable copy
        return

    @cached_property
    def columns(self):
        return [
            self._get_title_column("__str__"),
            Column("scheduled_publication_date"),
            Column("get_status_display", label=_("Status")),
            UpdatedAtColumn(),
            DateColumn(name="created_at", label=_("Added"), sort_key="created_at"),
            UserColumn("created_by", label=_("Added by")),
            DateColumn(name="approved_at", label=_("Approved at"), sort_key="approved_at"),
            UserColumn("approved_by"),
        ]


class BundleChooseView(ChooseView):
    icon = "boxes-stacked"

    @property
    def columns(self):
        return super().columns + [
            Column("scheduled_publication_date"),
            UserColumn("created_by"),
        ]

    def get_object_list(self):
        return Bundle.objects.select_related("created_by").only("name", "created_by")


class BundleChooserViewSet(ChooserViewSet):
    model = Bundle
    icon = "boxes-stacked"
    choose_view_class = BundleChooseView

    def get_object_list(self):
        return self.model.objects.editable()


class BundleViewSet(ModelViewSet):
    model = Bundle
    icon = "boxes-stacked"
    add_view_class = BundleCreateView
    edit_view_class = BundleEditView
    inspect_view_class = BundleInspectView
    index_view_class = BundleIndexView
    chooser_viewset_class = BundleChooserViewSet
    list_filter = ["status", "created_by"]
    add_to_admin_menu = True
    inspect_view_enabled = True


bundle_viewset = BundleViewSet("bundle")
bundle_chooser_viewset = BundleChooserViewSet("bundle_chooser")

BundleChooserWidget = bundle_chooser_viewset.widget_class
