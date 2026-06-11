from rest_framework import serializers

from authentication.models import User
from grantors.models import Grantors
from oipah.models import SectorAgricul
from plotLand.models import PlotLand
from project.models import CommissionProject, HistorikProject, ProjectCharge, ProjectModel, ProjectSubsidy


class CommissionProjectOtherSerializer(serializers.ModelSerializer):
    class Meta:
        model=CommissionProject
        exclude = ('oipah', 'created_at', 'updated')


class HistorikProjectOtherSerializer(serializers.ModelSerializer):
    class Meta:
        model=HistorikProject
        exclude = ('project',)


class SectorAgriculOtherSerializer(serializers.ModelSerializer):
    class Meta:
        model=SectorAgricul
        fields = ['id', 'name']
        

class UserMinSerializer(serializers.ModelSerializer):
    
    class Meta:
        model=User
        fields = ['id', 'name', 'surname', 'phone']
        

class PlotLandOtherSerializer(serializers.ModelSerializer):
    owner_land = UserMinSerializer()
    class Meta:
        model=PlotLand
        exclude = ('oipah', 'updated', 'date_add', 'date_owner', 'description', 'statut_land', 'acd_number',
                'filiere', 'source_water', 'type_ground', 'land_ownership')


class GrantorsOtherSerializer(serializers.ModelSerializer):
    
    class Meta:
        model=Grantors
        exclude = ('oipah', 'created_at', 'updated', 'country', 'email', 'type_donor', 'phone')
        

class ProjectSubsidyOtherSerializer(serializers.ModelSerializer):
    subsidy_name = serializers.CharField(source='subsidy.object')
    
    class Meta:
        model=ProjectSubsidy
        exclude = ('project', 'created_at')
        

class ProjectModelSerializer(serializers.ModelSerializer):
    filiere = SectorAgriculOtherSerializer(many=True)
    plot_land = PlotLandOtherSerializer()
    project_subsidies = ProjectSubsidyOtherSerializer(many=True,  read_only=True) #le related_name défini dans le modèle ProjectSubsidy
    
    class Meta:
        model=ProjectModel
        exclude = ('oipah', 'created_at', 'updated',)


class UserSerializerMini(serializers.ModelSerializer):
    class Meta:
        model=User
        fields = ['id', 'name', 'surname', 'phone']
        

class ProjectChargeSerializer(serializers.ModelSerializer):
    class Meta:
        model=ProjectCharge
        fields = ['id', 'label', 'amount', 'date']



