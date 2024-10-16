import csv
import io

from django.http import FileResponse, HttpRequest
from django.shortcuts import get_object_or_404
from rest_framework.decorators import action
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.serializers import ModelSerializer
from rest_framework.viewsets import ReadOnlyModelViewSet

from ons_alpha.charts.constants import DataSource
from ons_alpha.charts.models import Chart


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
    def data_csv(
        self,
        request: HttpRequest,  # pylint: disable=unused-argument
        uuid: str,
    ):
        chart = get_object_or_404(Chart, uuid=uuid).specific
        if chart.data_source == DataSource.CSV and chart.data_file:
            with open(chart.data_file, encoding="utf-8") as csvfile:
                return FileResponse(csvfile, filename="data.csv")
        if chart.data_source == DataSource.MANUAL and chart.manual_data:
            with io.StringIO(newline="") as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow([col["heading"] for col in chart.manual_data_table.columns])
                for row in chart.manual_data_table.row_data:
                    writer.writerow(row)
                return FileResponse(csvfile, filename="data.csv")
        return Response({"message": f"This endpoint is not supported for: {chart!r}"}, status=400)
