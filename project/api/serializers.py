from rest_framework import serializers

from grantors.models import Grantors, Subsidy
from oipah.models import SectorAgricul
from plotLand.models import PlotLand
from project.models import ProjectModel



class SectorAgriculOtherSerializer(serializers.ModelSerializer):
    class Meta:
        model=SectorAgricul
        fields = ['id', 'name']
        

class PlotLandOtherSerializer(serializers.ModelSerializer):
    class Meta:
        model=PlotLand
        exclude = ('oipah', 'updated', 'date_add', 'date_owner', 'description', 'statut_land', 'acd_number', 'owner_land',
                'filiere', 'source_water', 'type_ground', 'land_ownership')


class GrantorsOtherSerializer(serializers.ModelSerializer):
    
    class Meta:
        model=Grantors
        exclude = ('oipah', 'created_at', 'updated', 'country', 'email', 'type_donor', 'phone')
        

class SubsidyOtherSerializer(serializers.ModelSerializer):
    grantor = GrantorsOtherSerializer()
    filiere = SectorAgriculOtherSerializer(many=True)
    
    class Meta:
        model=Subsidy
        exclude = ('oipah', 'updated', 'status', 'received_date', 'reference', 'notes', 'advanced_amnt', 'rest_amnt', 'created_at')
        

class ProjectModelSerializer(serializers.ModelSerializer):
    filiere = SectorAgriculOtherSerializer(many=True)
    plot_land = PlotLandOtherSerializer()
    subsidies = SubsidyOtherSerializer(many=True)
    
    class Meta:
        model=ProjectModel
        exclude = ('oipah', 'created_at', 'updated',)




