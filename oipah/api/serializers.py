from rest_framework import serializers

from oipah.models import OipahAttribute


class OipahAttributeSerializer(serializers.ModelSerializer):
    class Meta:
        model=OipahAttribute
        exclude = ('updated', 'date_add')
        