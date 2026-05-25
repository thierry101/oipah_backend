from django.urls import path

from plotLand.api.views import PlotLandAPIView, PlotLandEditAPIView, PlotLandForProjectAPIView




urlpatterns = [
    path("plot-of-land", PlotLandAPIView.as_view(), name="plot-land"),
    path("plot-land-project/<id_usr>", PlotLandForProjectAPIView.as_view(), name="plot-land-projects"),
    path("edit-plot-of-land/<id_land>", PlotLandEditAPIView.as_view(), name="edit-plot-land"),
]
app_name = 'plotLand_route'

