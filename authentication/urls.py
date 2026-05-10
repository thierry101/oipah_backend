from django.urls import include, path



urlpatterns = [
    path("api/", include("authentication.api.urls", namespace="apiAuth")),
]
app_name = 'authenticationApi'