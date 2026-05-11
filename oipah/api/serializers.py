from rest_framework import serializers

from oipah.models import OipahAttribute, SectorAgricul


class OipahAttributeSerializer(serializers.ModelSerializer):
    class Meta:
        model=OipahAttribute
        exclude = ('updated', 'date_add')
  
        
class SectorAgriculSerializer(serializers.ModelSerializer):
    class Meta:
        model=SectorAgricul
        exclude = ('oipah', 'updated', 'date_add')