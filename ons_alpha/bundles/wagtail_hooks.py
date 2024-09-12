from functools import cached_property

from django.db.models import QuerySet
from django.http import HttpRequest
from django.urls import include, path
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _
from wagtail import hooks
from wagtail.admin.ui.components import Component
from wagtail.admin.widgets import PageListingButton
from wagtail.permission_policies import ModelPermissionPolicy

from . import admin_urls
from .models import Bundle, BundledPageMixin
from .viewsets import bundle_chooser_viewset, bundle_viewset


@hooks.register("register_admin_viewset")
def register_viewset():
    return [bundle_viewset, bundle_chooser_viewset]


class PageAddToBundleButton(PageListingButton):
    label = _("Add to Bundle")
    icon_name = "boxes-stacked"
    aria_label_format = _("Add '%(title)s' to a bundle")
    url_name = "bundles:add_to_bundle"

    @property
    def permission_policy(self):
        return ModelPermissionPolicy(Bundle)

    @property
    def show(self) -> bool:
        if not isinstance(self.page, BundledPageMixin):
            return False

        if self.page.in_active_bundle:
            return False

        # Note: limit to pages that are not in an active bundle
        return (
            self.page_perms.can_edit() or self.page_perms.can_publish()
        ) and self.permission_policy.user_has_any_permission(self.user, ["add", "change", "delete"])


@hooks.register("register_page_header_buttons")
def page_header_buttons(page, user, view_name, next_url=None):  # pylint: disable=unused-argument
    yield PageAddToBundleButton(page=page, user=user, priority=10, next_url=next_url)


@hooks.register("register_page_listing_buttons")
def page_listing_buttons(page, user, next_url=None):
    yield PageAddToBundleButton(page=page, user=user, priority=10, next_url=next_url)


@hooks.register("register_admin_urls")
def register_admin_urls():
    return [path("bundles/", include(admin_urls))]


@hooks.register("before_edit_page")
def preset_golive_date(request, page):  # pylint: disable=unused-argument
    if not isinstance(page, BundledPageMixin):
        return

    if not (page.in_active_bundle and page.active_bundle.scheduled_publication_date):
        return

    if now() < page.active_bundle.scheduled_publication_date != page.go_live_at:
        # pre-set the scheduled publishing time
        page.go_live_at = page.active_bundle.scheduled_publication_date


class LatestBundlesPanel(Component):
    name = "latest_bundles"
    order = 150
    template_name = "bundles/wagtailadmin/panels/latest_bundles.html"

    def __init__(self, request):
        self.request = request
        self.permission_policy = ModelPermissionPolicy(Bundle)

    @cached_property
    def is_shown(self) -> bool:
        return self.permission_policy.user_has_any_permission(self.request.user, {"add", "change", "delete"})

    def get_latest_bundles(self) -> QuerySet[Bundle]:
        if self.is_shown:
            return Bundle.objects.active().select_related("created_by")[:10]
        return Bundle.objects.none()

    def get_context_data(self, parent_context):
        context = super().get_context_data(parent_context)
        context["request"] = self.request
        context["bundles"] = self.get_latest_bundles()
        context["is_shown"] = self.is_shown
        return context


@hooks.register("construct_homepage_panels")
def add_another_welcome_panel(request: HttpRequest, panels: list[Component]):
    panels.append(LatestBundlesPanel(request))
