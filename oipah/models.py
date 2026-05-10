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
    logo = ResizedImageField(upload_to='logos', blank=True, null=True)
    date_add = models.DateTimeField(auto_now_add=True, db_index=True)
    updated = models.DateTimeField(auto_now=True)
    