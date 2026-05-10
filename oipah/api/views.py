from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.db import transaction

from authentication.permissions import AdminPermissions
from backend.regex import check_if_select_return_string, check_phone_numberRequired, checkIfEmailRequired, checkIfStringNotRequired, get_unique_oipah, validate_base64_image
from oipah.api.serializers import OipahAttributeSerializer
from oipah.models import OipahAttribute



class UpdateSettingAPIView(APIView):
    permission_classes = [AdminPermissions]
    
    def get(self, request):
        current_user = request.user
        try:
            oipah = OipahAttribute.objects.get(name=current_user.oipah.name)
        except OipahAttribute.DoesNotExist:
            pass
        serializer = OipahAttributeSerializer(oipah)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @transaction.atomic
    def put(self, request):
        current_user = request.user
        data = request.data
        errors = {}
        checker = data.get('checker')
        oipahs = OipahAttribute.objects.all().exclude(name=current_user.oipah.name)
        current_oipah = OipahAttribute.objects.filter(name=current_user.oipah.name)
        
        if checker == 'identity':
            oipah = get_unique_oipah("oipahName",oipahs, data.get('oipah'), errors, 'name')
            rccm = checkIfStringNotRequired(data.get('rccm'))
            niu = checkIfStringNotRequired(data.get('niu'))
            if not errors:
                update_oipah = current_oipah.first()
                update_oipah.name = oipah
                update_oipah.rccm = rccm
                update_oipah.niu = niu
                update_oipah.save()
                return Response({"result":True}, status=status.HTTP_200_OK)
            else:
                return Response({"errors":errors}, status=status.HTTP_400_BAD_REQUEST)
        
        if checker == 'contact':
            country = checkIfStringNotRequired(data.get('country'))
            city = checkIfStringNotRequired(data.get('city'))
            email = checkIfEmailRequired('email', data.get('email'), errors)
            phone = check_phone_numberRequired('phone', data.get('phone'), errors)
            if not errors:
                update_oipah = current_oipah.first()
                update_oipah.country = country
                update_oipah.city = city
                update_oipah.email = email
                update_oipah.phone = phone
                update_oipah.save()
                return Response({"result":True}, status=status.HTTP_200_OK)
            else:
                return Response({"errors":errors}, status=status.HTTP_400_BAD_REQUEST)
            
        if checker == 'preference':
            devise = check_if_select_return_string('devise', data.get('devise'), errors)
            item_per_page = check_if_select_return_string('item_per_page', data.get('itemPerPage'), errors)
            if not errors:
                update_oipah = current_oipah.first()
                update_oipah.devise = devise
                update_oipah.itemNber = item_per_page
                update_oipah.save()
                return Response({"result":True}, status=status.HTTP_200_OK)
            else:
                return Response({"errors":errors}, status=status.HTTP_400_BAD_REQUEST)
            
        if checker ==  'logo':
            image, extension = validate_base64_image('image', data.get('image'), errors)
            if not errors:
                update_oipah = current_oipah.first()
                # Supprime l'ancienne image si elle existe
                if update_oipah.logo:
                    update_oipah.logo.delete(save=False)
                # Sauvegarde la nouvelle image
                update_oipah.logo.save(image.name, image, save=True)
                
                return Response({"result":True}, status=status.HTTP_200_OK)
            else:
                return Response({"errors":errors}, status=status.HTTP_400_BAD_REQUEST)
            
        
        