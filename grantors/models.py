from decimal import Decimal

from django.db import models

from oipah.models import OipahAttribute, SectorAgricul

# Create your models here.


class Grantors(models.Model):
    oipah = models.ForeignKey(OipahAttribute, on_delete=models.CASCADE, blank=True, null=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    country = models.CharField(max_length=255, blank=True, null=True)
    email = models.CharField(max_length=255, blank=True, null=True)
    phone = models.CharField(max_length=255, blank=True, null=True)
    type_donor = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)
    
    
class Subsidy(models.Model):
    oipah = models.ForeignKey(OipahAttribute, on_delete=models.CASCADE, blank=True, null=True)
    grantor = models.ForeignKey(Grantors, on_delete=models.CASCADE, blank=True, null=True)
    object = models.CharField(max_length=255, blank=True, null=True)
    amount = models.DecimalField(blank=True, max_digits=12, decimal_places=2, null=True)
    dynamic_amount = models.DecimalField(blank=True, max_digits=12, decimal_places=2, null=True) #Montant disponible à linstant.
    status = models.CharField(max_length=255, blank=True, null=True)
    received_date = models.DateField(blank=True, null=True)
    reference = models.CharField(max_length=255, blank=True, null=True)
    filiere = models.ManyToManyField(SectorAgricul, blank=True)
    notes = models.TextField(blank=True, null=True)
    advanced_amnt = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    rest_amnt = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)
    
    def calculate_rest_amount(self):
        if self.amount is not None and self.status in ['partial', 'pending']:
            advanced = self.advanced_amnt or Decimal('0.00')
            self.rest_amnt = Decimal(self.amount) - Decimal(advanced)
        else:
            self.rest_amnt = 0

    def save(self, *args, **kwargs):
        self.calculate_rest_amount()
        super().save(*args, **kwargs)
    

class Commission_Dev(models.Model):
    oipah = models.ForeignKey(OipahAttribute, on_delete=models.CASCADE, blank=True, null=True)
    subsidy = models.ForeignKey(Subsidy, on_delete=models.CASCADE, blank=True, null=True)
    amount = models.DecimalField(blank=True, max_digits=12, decimal_places=2, null=True)
    advanced_amnt = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    status_comm = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)


class SubsidyPatial(models.Model):
    subsidy = models.ForeignKey(Subsidy, on_delete=models.CASCADE, blank=True, null=True)
    advanced_amnt = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    received_date = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)
    