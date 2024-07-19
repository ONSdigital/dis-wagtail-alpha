from typing import TYPE_CHECKING

from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from wagtail.admin import messages
from wagtail.models import Page

from .forms import AddToBundleForm
from .models import BundlePage


if TYPE_CHECKING:
    from django.http import HttpRequest


def add_to_bundle(request: "HttpRequest", page_to_add_id: "Page"):
    page_to_add = get_object_or_404(Page, id=page_to_add_id)
    page_perms = page_to_add.permissions_for_user(request.user)
    # note: add the relevant permission checks
    if not (page_perms.can_edit() or page_perms.can_publish()):
        raise PermissionDenied

    add_form = AddToBundleForm(
        request.POST or None,
        page_to_add=page_to_add,
    )

    next = None
    redirect_to = request.GET.get("next", None)
    if redirect_to and url_has_allowed_host_and_scheme(url=redirect_to, allowed_hosts={request.get_host()}):
        next = redirect_to

    if request.method == "POST":  # noqa SIM102
        if add_form.is_valid() and (bundle := add_form.cleaned_data.get("bundle")):
            if bundle.bundled_pages.filter(page=page_to_add).exists():
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
                redirect_to = request.POST.get("next", None)
                if redirect_to and url_has_allowed_host_and_scheme(url=redirect_to, allowed_hosts={request.get_host()}):
                    return redirect(redirect_to)
                else:
                    (reverse("wagtailadmin_explore", args=[page_to_add.get_parent().id]),)

    return TemplateResponse(
        request,
        "bundles/wagtailadmin/add_to_bundle.html",
        {
            "page_to_add": page_to_add,
            "add_form": add_form,
            "next": next,
        },
    )
