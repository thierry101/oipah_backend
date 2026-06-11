from django.db import models

from authentication.models import User
from grantors.models import Subsidy
from oipah.models import OipahAttribute, SectorAgricul, Vehicles
from plotLand.models import PlotLand

from django.core.exceptions import ValidationError
from django.db.models import Sum


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
    raw_amount = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    subsidies = models.ManyToManyField(Subsidy, through='ProjectSubsidy', null=True)
    submission_date = models.DateField(blank=True, null=True)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    nber_days = models.PositiveIntegerField(blank=True, null=True)
    qty = models.PositiveIntegerField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    purpose = models.TextField(blank=True, null=True)
    quantity_harvested = models.PositiveIntegerField(blank=True, null=True)
    harverst_date = models.DateField(blank=True, null=True)
    vehicle = models.ForeignKey(Vehicles, on_delete=models.SET_NULL, null=True)
    driver = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)
    
    
class ProjectCharge(models.Model):
    project = models.ForeignKey(ProjectModel, on_delete=models.CASCADE)
    label = models.CharField(max_length=255, blank=True, null=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    date = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)
    

class ProjectProducts(models.Model):
    project = models.ForeignKey(ProjectModel, on_delete=models.CASCADE)
    name = models.CharField(max_length=255, blank=True, null=True)
    qty = models.PositiveIntegerField(blank=True, null=True)
    unit = models.CharField(blank=True, null=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)
    
    
class HistorikProject(models.Model):
    project = models.ForeignKey(ProjectModel, on_delete=models.CASCADE)
    statut_project = models.CharField(max_length=255, blank=True, null=True)
    message = models.TextField(blank=True, null=True)
    changed_at = models.DateTimeField(auto_now_add=True)
    

class ProjectSubsidy(models.Model):
    project = models.ForeignKey(ProjectModel, on_delete=models.CASCADE, related_name='project_subsidies')
    subsidy = models.ForeignKey(Subsidy, on_delete=models.CASCADE, related_name='subsidy_projects')
    amount_used = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    amount_before = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    amount_after = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "project_subsidy"
        

class CommissionProject(models.Model):
    oipah = models.ForeignKey(OipahAttribute, on_delete=models.CASCADE, blank=True, null=True)
    title = models.CharField(max_length=255, blank=True, null=True)
    rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    is_entrepreneur = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)
    
    def clean(self):
        # Somme des rates
        total = CommissionProject.objects.exclude(id=self.id).aggregate(total=Sum('rate'))['total'] or 0

        if total + self.rate > 100:
            raise ValidationError({'rate': 'Le total des taux ne doit pas dépasser 100%.'})

        # Un seul entrepreneur
        if self.is_entrepreneur:
            exists = CommissionProject.objects.exclude(id=self.id).filter(
                is_entrepreneur=True).exists()

            if exists:
                raise ValidationError({
                    'is_entrepreneur': "On ne peut l'activer que pour une seule commission."})
    