from django.urls import include, path

from oipah.api.views import UpdateSettingAPIView



urlpatterns = [
    path("api/", include("grantors.api.urls", namespace="apigrantors")),

]
app_name = 'grantors_urls'