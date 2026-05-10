from django.urls import path

from authentication.api.views import RegisterUserAPIView, LoginUserViewAPIView, RegisterUserByAdmin, RegisterUserDetailAPIView, StateUserView
from rest_framework_simplejwt.views import TokenRefreshView


urlpatterns = [
    path("register", RegisterUserAPIView.as_view(), name="register"),
    path("register-user", RegisterUserByAdmin.as_view(), name="register-user"),
    path("login", LoginUserViewAPIView.as_view(), name="login"),
    path("refesh-token", TokenRefreshView.as_view(), name="refreshTokenAdmin"),
    path("state-user", StateUserView.as_view(), name="state-user"),
    path("edit-user/<id_user>", RegisterUserDetailAPIView.as_view(), name="edit-user"),
]
app_name = 'authentication'