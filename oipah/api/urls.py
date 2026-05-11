from django.urls import path

from oipah.api.views import SectorAgriculturalAPIView, SectorAgriculturalDetailAPIView, UpdateSettingAPIView



urlpatterns = [
    path("update-settings", UpdateSettingAPIView.as_view(), name="update-setting"),
    path("create-agricultural", SectorAgriculturalAPIView.as_view(), name="agricultural"),
    path("edit-agricultural/<id_sector>", SectorAgriculturalDetailAPIView.as_view(), name="edit-agricultural")

]
app_name = 'oipah'