from django.templatetags.static import static
from django.utils.html import format_html
from wagtail import hooks
from wagtail.snippets.models import register_snippet

from .admin_views import ChartViewSet


register_snippet(ChartViewSet)


@hooks.register('insert_editor_js')
def editor_js():
    return format_html(
        '<script src="{}"></script>', static("admin/charts/js/toggleDataSourceFields.js")
    )
