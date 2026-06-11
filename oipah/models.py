from django.db import models
from django_resized import ResizedImageField

# Create your models here.

class OipahAttribute(models.Model):
    name = models.CharField(max_length=100, null=True)
    rccm = models.CharField(max_length=100, blank=True, null=True)
    niu = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(max_length=255, db_index=True, blank=True, null=True)
    phone = models.CharField( max_length=50, db_index=True, null=True)
    devise = models.CharField(max_length=50, blank=True, null=True)
    itemNber = models.PositiveIntegerField(default=0)
    rate_dev = models.DecimalField(max_digits=5, decimal_places=2, default=1)
    logo = ResizedImageField(upload_to='logos', blank=True, null=True)
    date_add = models.DateTimeField(auto_now_add=True, db_index=True)
    updated = models.DateTimeField(auto_now=True)
    

class SectorAgricul(models.Model):
    oipah = models.ForeignKey(OipahAttribute, on_delete=models.CASCADE, blank=True, null=True)
    name = models.CharField(max_length=100, null=True)
    code_unik = models.CharField(max_length=100, null=True)
    description = models.TextField(blank=True, null=True)
    date_add = models.DateTimeField(auto_now_add=True, db_index=True)
    updated = models.DateTimeField(auto_now=True)
    

class Vehicles(models.Model):
    oipah = models.ForeignKey(OipahAttribute, on_delete=models.CASCADE, blank=True, null=True)
    # owner = models.ForeignKey('authentication.User', on_delete=models.CASCADE, blank=True, null=True)
    plate = models.CharField(max_length=100, null=True)
    model = models.CharField(max_length=100, null=True)
    type_vehicle = models.CharField(max_length=100, null=True)
    capacity = models.PositiveIntegerField(default=0)
    date_add = models.DateTimeField(auto_now_add=True, db_index=True)
    updated = models.DateTimeField(auto_now=True)
    
    