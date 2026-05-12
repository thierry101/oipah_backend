from django.urls import path

from plotLand.api.views import PlotLandAPIView




urlpatterns = [
    path("plot-of-land", PlotLandAPIView.as_view(), name="plot-land"),
]
app_name = 'plotLand_route'