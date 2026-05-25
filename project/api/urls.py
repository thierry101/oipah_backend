from django.urls import path

from project.api.views import ProjectAPIView




urlpatterns = [
    path("start-project", ProjectAPIView.as_view(), name="add-grantor"),
]
app_name = 'projects'