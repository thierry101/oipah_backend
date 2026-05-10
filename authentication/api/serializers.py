from rest_framework import serializers

from authentication.models import User
from oipah.api.serializers import OipahAttributeSerializer



class UserSerializer(serializers.ModelSerializer):
    oipah = OipahAttributeSerializer()
    class Meta:
        model=User
        fields = '__all__'
        extra_kwargs = {
            'password':{'write_only':True}
        }
        

class UserMiniSerializer(serializers.ModelSerializer):
    
    class Meta:
        model=User
        fields = ['id', 'name', 'surname', 'email', 'phone', 'role', 'type_doc', 'nber_doc', 'last_seen']
