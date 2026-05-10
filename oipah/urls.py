from django.urls import include, path



urlpatterns = [
    path("api/", include("oipah.api.urls", namespace="apiOipah")),
]
app_name = 'oipahApi'