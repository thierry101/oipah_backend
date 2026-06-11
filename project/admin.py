from django.contrib import admin

from project.models import HistorikProject, ProjectCharge, ProjectModel

# Register your models here.

admin.site.register(ProjectModel)
admin.site.register(HistorikProject)
admin.site.register(ProjectCharge)
