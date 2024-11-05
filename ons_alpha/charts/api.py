import csv
import io

from django.core.exceptions import PermissionDenied
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
        request: HttpRequest,
        uuid: str,
    ):
        chart = get_object_or_404(Chart, uuid=uuid).specific
        user = request.user
        if (chart.is_private or not chart.live) and (
            not user.is_authenticated
            or not chart.permission_policy.user_has_any_permission_for_instance(
                user, ["choose", "add", "change"], chart
            )
        ):
            raise PermissionDenied

        if chart.data_source == DataSource.CSV and chart.data_file:
            with open(chart.data_file, encoding="utf-8") as csvfile:
                return FileResponse(csvfile, filename="data.csv")

        if chart.data_source == DataSource.MANUAL and chart.data_manual:
            csvfile = io.StringIO()
            writer = csv.writer(csvfile)
            writer.writerow(chart.headers)
            for row in chart.manual_data_table.row_data:
                writer.writerow(row["values"])
            csvfile.seek(0)
            return FileResponse(csvfile.getvalue(), filename="data.csv", content_type="text/csv")

        return Response({"message": f"This endpoint is not supported for: {chart!r}"}, status=400)
