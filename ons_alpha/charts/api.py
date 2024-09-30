from django.shortcuts import get_object_or_404
from rest_framework.decorators import action
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.serializers import ModelSerializer
from rest_framework.viewsets import ReadOnlyModelViewSet

from .models import Chart


class ChartSerialzer(ModelSerializer):
    class Meta:
        model = Chart
        fields = ["name", "uuid"]


class ChartAPIViewSet(ReadOnlyModelViewSet):
    model = Chart
    queryset = Chart.objects.filter(live=True)
    serializer_class = ChartSerialzer
    renderer_classes = [JSONRenderer]
    lookup_field = "uuid"

    @action(detail=True, methods=["get"])
    def data(self, request, uuid: str):
        chart = get_object_or_404(Chart, uuid=uuid).specific
        return Response(chart.specific.get_data_json(request, for_data_api=True))
