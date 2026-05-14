from django.urls import path

from plotLand.api.views import PlotLandAPIView, PlotLandEditAPIView




urlpatterns = [
    path("plot-of-land", PlotLandAPIView.as_view(), name="plot-land"),
    path("edit-plot-of-land/<id_land>", PlotLandEditAPIView.as_view(), name="edit-plot-land"),
]
app_name = 'plotLand_route'