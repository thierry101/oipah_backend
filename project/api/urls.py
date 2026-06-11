from django.urls import path

from project.api.views import GetDriverAPIView, GetEndedProjectAPIView, GetProjectUserAPIView, ProjectAPIView, ProjectDetailAPIView, ProjectFinalizeAPIView, SettingCommissionAPIView, SettingCommissionDetailAPIView




urlpatterns = [
    path("start-project", ProjectAPIView.as_view(), name="add-grantor"),
    path("delete-update-project/<id_project>", ProjectDetailAPIView.as_view(), name="delete-project"),
    path("setting-commission", SettingCommissionAPIView.as_view(), name="set-comm"),
    path("delete-update-commission/<id_commission>", SettingCommissionDetailAPIView.as_view(), name="del-upd-comm"),
    path("get-ended-project", GetEndedProjectAPIView.as_view(), name="ended-projects"),
    path("get-drivers", GetDriverAPIView.as_view(), name="get-drivers"),
    path("get-project-users", GetProjectUserAPIView.as_view(), name="get-project-users"),
    path("finalize-project/<id_project>", ProjectFinalizeAPIView.as_view(), name="finalize-project"),
]
app_name = 'projects'