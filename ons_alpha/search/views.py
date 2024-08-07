from django.conf import settings
from django.core.paginator import Paginator
from django.template.response import TemplateResponse
from django.utils.cache import add_never_cache_headers, patch_cache_control
from wagtail.models import Page

from ons_alpha.utils.cache import get_default_cache_control_kwargs


def search(request):
    search_query = request.GET.get("query", None)
    page = request.GET.get("page", 1)

    # Search
    search_results = Page.objects.live().search(search_query, operator="and") if search_query else Page.objects.none()

    # Pagination
    search_results = Paginator(search_results, settings.DEFAULT_PER_PAGE).get_page(page)

    response = TemplateResponse(
        request,
        "templates/pages/search/search.html",
        {"search_query": search_query, "search_results": search_results},
    )
    # Instruct FE cache to not cache when the search query is present.
    # It's so hits get added to the database and results include newly
    # added pages.
    if search_query:
        add_never_cache_headers(response)
    else:
        patch_cache_control(response, **get_default_cache_control_kwargs())
    return response
