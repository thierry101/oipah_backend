from django.urls import path

from grantors.api.views import GrantorsAPIView, GrantorsDetailAPIView, SubsidyAPIView, SubsidyDetailAPIView, SubsidyForProjectAPIView, SubsidyPartialAPIView



urlpatterns = [
    path("register-grantor", GrantorsAPIView.as_view(), name="add-grantor"),
    path("edit-grantor/<id_grantor>", GrantorsDetailAPIView.as_view(), name="edit-grantor"),
    path("register-subsidy", SubsidyAPIView.as_view(), name="add-subsidy"),
    path("subsidy-project", SubsidyForProjectAPIView.as_view(), name="project-subsidy"),
    path("edit-subsidy/<id_subsidy>", SubsidyDetailAPIView.as_view(), name="edit-subsidy"),
    path("partial-subsidy/<id_subsidy>", SubsidyPartialAPIView.as_view(), name="partial-subsidy"),
]
app_name = 'grantors'