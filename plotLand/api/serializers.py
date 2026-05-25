from rest_framework import serializers

from authentication.models import User
from oipah.api.serializers import SectorAgriculSerializer
from oipah.models import SectorAgricul
from plotLand.models import PlotLand


class UserMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model=User
        fields = ['id', 'name', 'surname', 'phone']

        
class PlotLandSerializer(serializers.ModelSerializer):
    owner_land = UserMiniSerializer()
    filiere = SectorAgriculSerializer()
    class Meta:
        model=PlotLand
        exclude = ('oipah', 'updated', 'date_add')


class SectorAgriculMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model=SectorAgricul
        fields = ['name']
        

class PlotLandMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model=PlotLand
        exclude = ('oipah', 'updated', 'date_add', 'date_owner', 'description',
                'statut_land', 'acd_number', 'owner_land', 'filiere')