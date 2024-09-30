from wagtail.snippets.models import register_snippet

from .admin_views import ChartViewSet


register_snippet(ChartViewSet)
