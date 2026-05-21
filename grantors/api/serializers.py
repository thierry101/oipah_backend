from rest_framework import serializers

from grantors.models import Grantors, Subsidy, SubsidyPatial
from oipah.api.serializers import SectorAgriculSerializer



class GrantorsSerializer(serializers.ModelSerializer):
    
    class Meta:
        model=Grantors
        exclude = ('oipah', 'created_at', 'updated',)
        

class SubsidySerializer(serializers.ModelSerializer):
    grantor = GrantorsSerializer()
    filiere = SectorAgriculSerializer(many=True)
    
    class Meta:
        model=Subsidy
        exclude = ('oipah', 'updated',)


class SubsidyPatialSerializer(serializers.ModelSerializer):
    
    class Meta:
        model=SubsidyPatial
        exclude = ('created_at', 'updated', 'subsidy')

