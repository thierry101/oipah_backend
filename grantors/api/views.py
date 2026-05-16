from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Sum

from authentication.permissions import AdminPermissions
from backend.regex import check_amount, check_if_select_return_string, check_is_date_required, check_multi_select_list_required, check_phone_number_not_required, checkIfEmailNotRequired, checkIfStringNotRequired, checkIfStringRequired
from backend.utils.custom_pagination import CustomPagination
from grantors.api.serializers import GrantorsSerializer, SubsidySerializer
from grantors.models import Grantors, Subsidy




class GrantorsAPIView(APIView):
    permission_classes = [AdminPermissions]
    
    def get(self, request):
        current_user = request.user
        search = request.GET.get('search', '').strip()
        donors = Grantors.objects.filter(oipah=current_user.oipah)
        if search:
            donors = donors.filter(name__icontains=search)
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
        

class GrantorsDetailAPIView(APIView):
    permission_classes = [AdminPermissions]
    
    def put(self, request, id_grantor):
        current_user = request.user
        data = request.data
        errors = {}
        name = checkIfStringRequired('name', data.get('name'), errors)
        type_donor = check_if_select_return_string('type_donor', data.get('type_donor'), errors)
        country = check_if_select_return_string('country', data.get('country'), errors)
        email = checkIfEmailNotRequired('email', data.get('email'), errors)
        phone = check_phone_number_not_required('phone', data.get('phone'), errors)
        try:
            grantor = Grantors.objects.get(id=int(id_grantor), oipah=current_user.oipah)
        except Grantors.DoesNotExist:
            errors['grantor'] = "Ce subventionneur n'existe pas"
        if grantor and name and (name != grantor.name):
            if Grantors.objects.filter(oipah=current_user.oipah, name=name).exists():
                errors['name'] = "Ce subventionneur existe déjà"
        if not errors:
            grantor.name = name
            grantor.type_donor = type_donor
            grantor.country = country
            grantor.email = email
            grantor.phone = phone
            grantor.save()
            return Response({'result':True}, status=status.HTTP_200_OK)
        else:
            return Response({'errors':errors}, status=status.HTTP_400_BAD_REQUEST)
        
    def delete(self, request, id_grantor):
        current_user = request.user
        errors = {}
        try:
            grantor = Grantors.objects.get(id=int(id_grantor), oipah=current_user.oipah)
        except Grantors.DoesNotExist:
            errors['grantor'] = "Ce subventionneur n'existe pas"
        if grantor:
            grantor.delete()
        return Response({'result':True}, status=status.HTTP_200_OK)
    

class SubsidyAPIView(APIView):
    permission_classes = [AdminPermissions]
    
    def get(self, request):
        current_user = request.user
        subsidies = Subsidy.objects.filter(oipah=current_user.oipah)
        paginator = CustomPagination()
        
        total_received = subsidies.filter(oipah=current_user.oipah, status="received").aggregate(total=Sum('amount'))['total'] or 0
        total_pending = subsidies.filter(oipah=current_user.oipah, status="pending").aggregate(total=Sum('amount'))['total'] or 0
        others = {'total_received':total_received, 'total_pending':total_pending}
        result_page = paginator.paginate_queryset(subsidies, request)
        serializer = SubsidySerializer( result_page, many=True)
        response = paginator.get_paginated_response(serializer.data)
        response.data['other_params'] = others
        return response
        
    def post(self, request):
        advanced_amnt = None
        current_user = request.user
        data = request.data
        errors = {}
        donor_id = check_if_select_return_string('donorId', data.get('donorId'), errors)
        object = checkIfStringRequired('object', data.get('object'), errors)
        amount = check_amount('amount', data.get('amount'), errors)
        statut = check_if_select_return_string('status', data.get('status'), errors)
        received_date = check_is_date_required('receivedDate', data.get('received_date'), errors)
        reference = checkIfStringNotRequired('reference')
        filiere = check_multi_select_list_required('filiere', data.get('filiere'), errors)
        notes = checkIfStringNotRequired('notes')
        if statut == 'partial':
            advanced_amnt = check_amount('advancedAmnt', data.get('advanced_amnt'), errors)
        if not errors:
            subsidy = Subsidy.objects.create(oipah=current_user.oipah, grantor_id=int(donor_id), object=object, notes=notes,
                    amount=amount, status=statut, received_date=received_date, reference=reference, advanced_amnt=advanced_amnt)
            for fil in filiere:
                subsidy.filiere.add(fil)
            return Response({'result':True}, status=status.HTTP_200_OK)
        else:
            return Response({'errors':errors}, status=status.HTTP_400_BAD_REQUEST)
    

class SubsidyDetailAPIView(APIView):
    permission_classes = [AdminPermissions]
    
    def put(self, request, id_subsidy):
        current_user = request.user
        data = request.data
        print(data)
        errors = {}
        if not errors:
        
            return Response({'result':True}, status=status.HTTP_200_OK)
        else:
            return Response({'errors':errors}, status=status.HTTP_400_BAD_REQUEST)
        
    