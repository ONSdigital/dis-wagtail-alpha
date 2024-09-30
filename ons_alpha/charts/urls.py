from rest_framework import routers

from ons_alpha.charts.api import ChartAPIViewSet


app_name = "charts-api"

router = routers.DefaultRouter()
router.register(r"charts", ChartAPIViewSet)

urlpatterns = router.urls
