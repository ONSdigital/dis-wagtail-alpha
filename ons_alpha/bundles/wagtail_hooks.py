from django.contrib.auth.models import Permission
from django.urls import include, path
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _
from wagtail import hooks
from wagtail.admin.widgets import PageListingButton

from . import admin_urls
from .models import BundledPageMixin
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
    def show(self) -> bool:
        if not isinstance(self.page, BundledPageMixin):
            return False

        if self.page.in_active_bundle:
            return False

        # Note: limit to pages that are not in an active bundle
        return self.page_perms.can_edit() or self.page_perms.can_publish()


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


@hooks.register("register_permissions")
def register_bundle_permissions():
    model = "bundle"

    return Permission.objects.filter(
        content_type__app_label="bundles",
        codename__in=[f"view_{model}", f"add_{model}", f"change_{model}", f"delete_{model}"],
    )
