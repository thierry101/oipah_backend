from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from authentication.permissions import AdminPermissions
from backend.regex import check_if_select_return_string, check_phone_number_not_required, checkIfEmailNotRequired, checkIfStringRequired
from backend.utils.custom_pagination import CustomPagination
from grantors.api.serializers import GrantorsSerializer
from grantors.models import Grantors




class GrantorsAPIView(APIView):
    permission_classes = [AdminPermissions]
    
    def get(self, request):
        current_user = request.user
        donors = Grantors.objects.filter(oipah=current_user.oipah)
        paginator = CustomPagination()
        result_page = paginator.paginate_queryset(donors, request)
        serializer = GrantorsSerializer( result_page, many=True)
        return paginator.get_paginated_response( serializer.data)
    
    def post(self, request):
        current_user = request.user
        data = request.data
        errors = {}
        name = checkIfStringRequired('name', data.get('name'), errors)
        type_donor = check_if_select_return_string('type_donor', data.get('type_donor'), errors)
        country = check_if_select_return_string('country', data.get('country'), errors)
        email = checkIfEmailNotRequired('email', data.get('email'), errors)
        phone = check_phone_number_not_required('phone', data.get('phone'), errors)
        if not errors:
            Grantors.objects.create(oipah=current_user.oipah, name=name, type_donor=type_donor, country=country,
                                    email=email, phone=phone)
            return Response({"result":True}, status=status.HTTP_201_CREATED)
        else:
            return Response({'errors':errors}, status=status.HTTP_400_BAD_REQUEST)