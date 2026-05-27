from django.urls import path

from project.api.views import ProjectAPIView, ProjectDetailAPIView




urlpatterns = [
    path("start-project", ProjectAPIView.as_view(), name="add-grantor"),
    path("delete-update-project/<id_project>", ProjectDetailAPIView.as_view(), name="delete-project"),
]
app_name = 'projects'