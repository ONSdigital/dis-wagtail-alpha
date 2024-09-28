from wagtail.snippets.models import register_snippet

from .views import ChartViewSet


register_snippet(ChartViewSet)
