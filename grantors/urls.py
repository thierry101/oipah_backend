from django.urls import include, path


urlpatterns = [
    path("api/", include("grantors.api.urls", namespace="apigrantors")),

]
app_name = 'grantors_urls'