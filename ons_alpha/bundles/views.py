from typing import TYPE_CHECKING

from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from wagtail.admin import messages
from wagtail.models import Page
from wagtail.permission_policies import ModelPermissionPolicy

from .admin_forms import AddToBundleForm
from .models import Bundle, BundledPageMixin, BundlePage


if TYPE_CHECKING:
    from django.http import HttpRequest


def add_to_bundle(request: "HttpRequest", page_to_add_id: int):
    page_to_add = get_object_or_404(Page.objects.specific(), id=page_to_add_id)

    if not isinstance(page_to_add, BundledPageMixin):
        raise Http404("Cannot add this page type to a bundle")

    if not has_permission(request, page_to_add):
        raise PermissionDenied

    if page_to_add.in_active_bundle:
        handle_existing_bundle(request, page_to_add)
        return redirect("wagtailadmin_home")

    return handle_add_to_bundle(request, page_to_add)


def has_permission(request, page_to_add):
    page_perms = page_to_add.permissions_for_user(request.user)
    if not (page_perms.can_edit() or page_perms.can_publish()):
        return False

    permission_policy = ModelPermissionPolicy(Bundle)
    return permission_policy.user_has_permission(request.user, "change")


def handle_existing_bundle(request, page_to_add):
    bundles = ", ".join(list(page_to_add.active_bundles.values_list("name", flat=True)))
    messages.warning(request, f"Page {page_to_add.get_admin_display_title()} is already in a bundle ('{bundles}')")


def handle_add_to_bundle(request, page_to_add):
    goto_next = get_redirect_url(request)
    add_form = AddToBundleForm(request.POST or None, page_to_add=page_to_add)

    if request.method == "POST" and add_form.is_valid():
        bundle = add_form.cleaned_data.get("bundle")
        if bundle and bundle.bundled_pages.filter(page=page_to_add).exists():
            messages.error(request, f"Page {page_to_add.get_admin_display_title()} is already in bundle '{bundle}'")
        else:
            bundle.bundled_pages.add(BundlePage(page=page_to_add))
            bundle.save()
            messages.success(
                request,
                f"Page '{page_to_add.get_admin_display_title()}' added to bundle '{bundle}'",
                buttons=[
                    messages.button(
                        reverse("wagtailadmin_pages:edit", args=(page_to_add.id,)),
                        "Edit",
                    )
                ],
            )
            return redirect_to_next(request, page_to_add)

    return TemplateResponse(
        request,
        "bundles/wagtailadmin/add_to_bundle.html",
        {
            "page_to_add": page_to_add,
            "add_form": add_form,
            "next": goto_next,
        },
    )


def get_redirect_url(request):
    redirect_to = request.GET.get("next", None)
    if redirect_to and url_has_allowed_host_and_scheme(url=redirect_to, allowed_hosts={request.get_host()}):
        return redirect_to
    return None


def redirect_to_next(request, page_to_add):
    redirect_to = request.POST.get("next", None)
    if redirect_to and url_has_allowed_host_and_scheme(url=redirect_to, allowed_hosts={request.get_host()}):
        return redirect(redirect_to)
    return redirect("wagtailadmin_explore", page_to_add.get_parent().id)
