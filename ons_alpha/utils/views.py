import logging

from http import HTTPStatus

from django.conf import settings
from django.shortcuts import render
from django.views import defaults
from django.views.generic import TemplateView


def page_not_found(request, exception, template_name="templates/pages/errors/404.html"):
    return defaults.page_not_found(request, exception, template_name)


def server_error(request, template_name="templates/pages/errors/500.html"):
    return defaults.server_error(request, template_name)


def csrf_failure(
    request,
    reason: str = "",  # given by Django
    template_name: str = "templates/pages/errors/403.html",
):
    csrf_logger = logging.getLogger("django.security.csrf")
    csrf_logger.exception("CSRF Failure: %s", reason)

    return render(request, template_name, status=HTTPStatus.FORBIDDEN)


class ManageCookieSettingsView(TemplateView):
    template_name = "templates/pages/manage_cookie_settings.html"

    def get_context_data(self, **kwargs):
        from ons_alpha.standardpages.models import InformationPage

        context = super().get_context_data(**kwargs)
        context["page"] = InformationPage(id=0, title=f"Cookies on {self.request.get_host()}")
        return context
