from django.urls import path

from grantors.api.views import GrantorsAPIView, GrantorsDetailAPIView



urlpatterns = [
    path("register-grantor", GrantorsAPIView.as_view(), name="add-grantor"),
    path("edit-grantor/<id_grantor>", GrantorsDetailAPIView.as_view(), name="edit-grantor"),
]
app_name = 'grantors'