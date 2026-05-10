from django.urls import path

from oipah.api.views import UpdateSettingAPIView



urlpatterns = [
    path("update-settings", UpdateSettingAPIView.as_view(), name="update-setting6+"),

]
app_name = 'oipah'