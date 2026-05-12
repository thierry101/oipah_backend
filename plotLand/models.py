from django.db import models

from authentication.models import User
from oipah.models import OipahAttribute, SectorAgricul

# Create your models here.


class PlotLand(models.Model):
    oipah = models.ForeignKey(OipahAttribute, on_delete=models.CASCADE, blank=True, null=True)
    owner_land = models.ForeignKey(User, blank=True, on_delete=models.CASCADE, null=True)
    code_land = models.CharField(max_length=100, null=True)
    statut_land = models.CharField(max_length=100, null=True)
    filiere = models.ForeignKey(SectorAgricul, on_delete=models.CASCADE, blank=True, null=True)
    area = models.FloatField(blank=True, null=True)
    department = models.CharField(max_length=100, null=True)
    sub_prefecture = models.CharField(max_length=100, null=True)
    quater = models.CharField(max_length=100, null=True)
    gps = models.CharField(max_length=100, null=True)
    land_ownership = models.CharField(max_length=255, blank=True, null=True)
    acd_number = models.CharField(max_length=255, blank=True, null=True)
    type_ground = models.CharField(max_length=255, blank=True, null=True)
    source_water = models.CharField(max_length=255, blank=True, null=True)
    date_owner = models.DateField(blank=True, null=True)
    description = models.TextField(max_length=255, blank=True, null=True)
    date_add = models.DateTimeField(auto_now_add=True, db_index=True)
    updated = models.DateTimeField(auto_now=True)
    
    