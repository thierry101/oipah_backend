from rest_framework import serializers

from grantors.models import Grantors



class GrantorsSerializer(serializers.ModelSerializer):
    
    class Meta:
        model=Grantors
        exclude = ('oipah', 'created_at', 'updated')
