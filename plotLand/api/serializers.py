from rest_framework import serializers

from authentication.models import User
from oipah.api.serializers import SectorAgriculSerializer
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