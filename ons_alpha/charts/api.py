from rest_framework.decorators import action
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet

from .models import Chart


class ChartAPIViewSet(ReadOnlyModelViewSet):
    model = Chart
    queryset = Chart.objects.filter(live=True)
    renderer_classes = [JSONRenderer]

    @action(detail=True, methods=["get"])
    def serve_data(self, request):
        chart = self.get_object().specific
        return Response(chart.specific.get_data_json(request))
