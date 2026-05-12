from django.urls import include, path



urlpatterns = [
    path("api/", include("plotLand.api.urls", namespace="apiplotLand")),
]
app_name = 'plotLandApi'