from django.db import models

from grantors.models import Subsidy
from oipah.models import OipahAttribute, SectorAgricul
from plotLand.models import PlotLand

# Create your models here.

class ProjectModel(models.Model):
    oipah = models.ForeignKey(OipahAttribute, on_delete=models.CASCADE, blank=True, null=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    type_project = models.CharField(max_length=255, blank=True, null=True)
    modeExecution = models.CharField(max_length=255, blank=True, null=True)
    filiere = models.ManyToManyField(SectorAgricul, null=True)
    current_statut = models.CharField(max_length=255, blank=True, null=True)
    plot_land = models.ForeignKey(PlotLand, on_delete=models.SET_NULL, null=True)
    budget = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    cost_per_ha = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    subsidies = models.ManyToManyField(Subsidy, blank=True)
    submission_date = models.DateField(blank=True, null=True)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    nber_days = models.PositiveIntegerField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    purpose = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)
    