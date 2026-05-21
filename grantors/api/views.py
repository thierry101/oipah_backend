from decimal import Decimal

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from django.db.models import DecimalField, Sum, Q, Value
from django.db.models.functions import Coalesce

from authentication.permissions import AdminPermissions
from backend.regex import check_amount, check_if_select_return_string, check_is_date_required, check_multi_select_list_required, check_phone_number_not_required, checkIfEmailNotRequired, checkIfStringNotRequired, checkIfStringRequired, convert_string_to_date
from backend.utils.custom_pagination import CustomPagination
from grantors.api.serializers import GrantorsSerializer, SubsidyPatialSerializer, SubsidySerializer
from grantors.models import Grantors, Subsidy, SubsidyPatial


class GrantorsAPIView(APIView):
    permission_classes = [AdminPermissions]
    
    def get(self, request):
        current_user = request.user
        search = request.GET.get('search', '').strip()
        donors = Grantors.objects.filter(oipah=current_user.oipah).order_by('-updated')
        if search:
            donors = donors.filter(name__icontains=search)
        paginator = CustomPagination()
        result_page = paginator.paginate_queryset(donors, request)
        serializer = GrantorsSerializer( result_page, many=True)
        return paginator.get_paginated_response( serializer.data)
    
    @transaction.atomic
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
        paginator = CustomPagination()
        subsidies = Subsidy.objects.filter(oipah=current_user.oipah).order_by('-updated')
        search = request.GET.get('search', '').strip()
        statut = request.GET.get('statut_land', '').strip()
        start_date = request.GET.get('start_date', '').strip()
        end_date = request.GET.get('end_date', '').strip()
        decimal_field = DecimalField(max_digits=12, decimal_places=2)
        
        if search:
            subsidies = subsidies.filter(Q(grantor__name__icontains=search) | Q(filiere__name__icontains=search))
        if statut:
            subsidies = subsidies.filter(status=statut)
        if start_date and end_date and (convert_string_to_date(start_date) < convert_string_to_date(end_date)):
            subsidies = subsidies.filter(received_date__gte=start_date, received_date__lte=end_date)
        
        # total_received = subsidies.filter(oipah=current_user.oipah, status="received").aggregate(total=Sum('amount'))['total'] or 0

        received_amount = subsidies.filter(oipah=current_user.oipah, status="received").aggregate(
        total=Coalesce(Sum('amount'), Value(0, output_field=decimal_field)))['total']
        partial_advanced = subsidies.filter(oipah=current_user.oipah, status="partial").aggregate(
        total=Coalesce(Sum('advanced_amnt'), Value(0, output_field=decimal_field)))['total']
        total_received = received_amount + partial_advanced
        total_pending = subsidies.filter(oipah=current_user.oipah, status="pending").aggregate(total=Sum('amount'))['total'] or 0
        others = {'total_received':total_received, 'total_pending':total_pending}
        result_page = paginator.paginate_queryset(subsidies, request)
        serializer = SubsidySerializer( result_page, many=True)
        response = paginator.get_paginated_response(serializer.data)
        response.data['other_params'] = others
        return response
        
    @transaction.atomic
    def post(self, request):
        advanced_amnt = None
        current_user = request.user
        data = request.data
        errors = {}
        donor_id = check_if_select_return_string('donorId', data.get('donorId'), errors)
        object = checkIfStringRequired('object', data.get('object'), errors)
        amount = check_amount('amount', data.get('amount'), errors)
        statut = check_if_select_return_string('status', data.get('status'), errors)
        if statut != 'pending':
            received_date = check_is_date_required('receivedDate', data.get('received_date'), errors)
        else:
            received_date = None
        reference = checkIfStringNotRequired('reference')
        filiere = check_multi_select_list_required('filiere', data.get('filiere'), errors)
        notes = checkIfStringNotRequired('notes')
        if statut == 'partial':
            advanced_amnt = check_amount('advancedAmnt', data.get('advanced_amnt'), errors)
            if advanced_amnt and amount and (Decimal(advanced_amnt) > Decimal(amount)):
                errors['advancedAmnt'] = "Ce montant ne peut être supérieur au montant de la subvention"
        if not errors:
            subsidy = Subsidy.objects.create(oipah=current_user.oipah, grantor_id=int(donor_id), object=object, notes=notes,
                    amount=amount, status=statut, received_date=received_date, reference=reference, advanced_amnt=advanced_amnt)
            if statut in ['partial', 'pending']:
                SubsidyPatial.objects.create(subsidy=subsidy, advanced_amnt=advanced_amnt or 0, received_date=received_date)
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
        errors = {}
        donor_id = check_if_select_return_string('donorId', data.get('donorId'), errors)
        object = checkIfStringRequired('object', data.get('object'), errors)
        statut = check_if_select_return_string('status', data.get('status'), errors)
        if statut != 'pending':
            received_date = check_is_date_required('receivedDate', data.get('received_date'), errors)
        reference = checkIfStringNotRequired('reference')
        filiere = check_multi_select_list_required('filiere', data.get('filiere'), errors)
        notes = checkIfStringNotRequired('notes')
        try:
            subsidy = Subsidy.objects.get(oipah=current_user.oipah, id=int(id_subsidy))
        except Subsidy.DoesNotExist:
            errors['donorId'] = "Cette subvention n'existe pas"
        if not errors:
            subsidy.grantor_id=int(donor_id)
            subsidy.object = object
            subsidy.received_date = received_date or None
            subsidy.reference = reference
            subsidy.notes = notes
            subsidy.filiere.set(filiere)
            subsidy.save()
            return Response({'result':True}, status=status.HTTP_200_OK)
        else:
            return Response({'errors':errors}, status=status.HTTP_400_BAD_REQUEST)
        
    def delete(self, request, id_subsidy):
        current_user = request.user
        errors = {}
        try:
            subsidy = Subsidy.objects.get(oipah=current_user.oipah, id=int(id_subsidy))
        except Subsidy.DoesNotExist:
            errors['donorId'] = "Cette subvention n'existe pas"
        if subsidy:
            SubsidyPatial.objects.filter(subsidy=subsidy).delete()
            subsidy.delete()
        return Response({'result':True}, status=status.HTTP_200_OK)
            
        
class SubsidyPartialAPIView(APIView):
    permission_classes = [AdminPermissions]
    
    def get(self, request, id_subsidy):
        partial_subsidies = SubsidyPatial.objects.filter(subsidy_id=int(id_subsidy))
        serializer = SubsidyPatialSerializer(partial_subsidies, many=True)
        return Response({'result':serializer.data}, status=status.HTTP_200_OK)
    
    
    @transaction.atomic
    def post(self, request, id_subsidy):
        current_user = request.user
        errors = {}
        try:
            subsidy = Subsidy.objects.get(oipah=current_user.oipah, id=int(id_subsidy))
        except Subsidy.DoesNotExist:
            subsidy = None
        if subsidy:
            data = request.data
            amount = check_amount('amount', data.get('amount'), errors)
            received_date = check_is_date_required('receivedDate', data.get('received_date'), errors)
            advanc_amnt = subsidy.advanced_amnt or 0
            if amount and (advanc_amnt + Decimal(amount) > subsidy.amount):
                errors['amount'] = "Le cumul des montants dépasse le montant total de la subvention"
            if not errors:
                SubsidyPatial.objects.create(subsidy_id=int(id_subsidy), advanced_amnt=amount, received_date=received_date)
                subsidy.advanced_amnt = (subsidy.advanced_amnt or Decimal('0')) + Decimal(amount)
                subsidy.save()
                if subsidy.advanced_amnt >= subsidy.amount:
                    subsidy.status = "received"
                else:
                    subsidy.status = "partial"
                subsidy.save()
                return Response({'result':True}, status=status.HTTP_200_OK)
            else:
                return Response({'errors':errors}, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, id_subsidy):
        current_user = request.user
        try:
            partial_subsidy = SubsidyPatial.objects.get(id=int(id_subsidy))
        except SubsidyPatial.DoesNotExist:
            partial_subsidy = None
        if partial_subsidy:
            partial_subsidy.subsidy.advanced_amnt -= partial_subsidy.advanced_amnt
            partial_subsidy.subsidy.status = "partial"
            partial_subsidy.subsidy.save()
            partial_subsidy.delete()
            return Response({'result':True}, status=status.HTTP_200_OK)
        