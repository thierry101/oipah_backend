from django.urls import path

from grantors.api.views import GrantorsAPIView



urlpatterns = [
    path("register-grantor", GrantorsAPIView.as_view(), name="add-grantor"),
]
app_name = 'grantors'