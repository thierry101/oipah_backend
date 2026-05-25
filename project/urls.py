from django.urls import include, path




urlpatterns = [
    path("api/", include("project.api.urls", namespace="apiproject")),

]
app_name = 'project_urls'