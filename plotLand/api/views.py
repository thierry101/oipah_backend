from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Sum, Q
from rest_framework.permissions import IsAuthenticated

from backend.regex import check_if_select_return_string, check_int_or_float, check_is_date_not_required, checkIfStringNotRequired, checkIfStringRequired, get_unique_name
from backend.utils.custom_pagination import CustomPagination
from plotLand.api.serializers import PlotLandSerializer
from plotLand.models import PlotLand



class PlotLandAPIView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        current_user = request.user
        search = request.GET.get('search', '').strip()
        statutLand = request.GET.get('statut_land', '').strip()
        if current_user.role == 'Admin':
            lands = PlotLand.objects.filter(oipah=current_user.oipah)
        if current_user.role == 'Agricultural':
            lands = PlotLand.objects.filter(oipah=current_user.oipah, owner_land=current_user)
        if search:
                lands = lands.filter(Q(department__icontains=search) | Q(sub_prefecture__icontains=search) | Q(quater__icontains=search))
        if statutLand:
            lands = lands.filter(statut_land__icontains=statutLand)
        
        paginator = CustomPagination()
        total_area = lands.aggregate(total=Sum('area'))['total'] or 0
        total_active = lands.filter(statut_land='active').count()
        total_unique_owners = lands.values('owner_land').distinct().count()
        result_page = paginator.paginate_queryset(lands, request)
        serializer = PlotLandSerializer(result_page, many=True)
        others = {"total_area": total_area, "total_active": total_active, "total_unique_owners": total_unique_owners}
        # Réponse paginée
        response = paginator.get_paginated_response(serializer.data)
        response.data['other_params'] = others
        return response

    def post(self, request):
        current_user = request.user
        data = request.data
        errors = {}
        lands = PlotLand.objects.filter(oipah=current_user.oipah)
        if current_user.role == 'Admin':
            owner = check_if_select_return_string('owner_land', data.get('owner_land'), errors)
        departement = checkIfStringRequired('department', data.get('department'), errors)
        sousPrefecture = checkIfStringRequired('sub_prefecture', data.get('sub_prefecture'), errors)
        village = checkIfStringRequired('quater', data.get('quater'), errors)
        gps = checkIfStringNotRequired(data.get('gps'))
        superficie = check_int_or_float('area', data.get('area'), errors)
        filiere = check_if_select_return_string('filiere', data.get('filiere'), errors)
        typeSol = check_if_select_return_string('type_ground', data.get('type_ground'), errors)
        sourceEau = check_if_select_return_string('source_water', data.get('source_water'), errors)
        tenureFonciere = check_if_select_return_string('land_ownership', data.get('land_ownership'), errors)
        titreFoncier = checkIfStringNotRequired(data.get('acd_number'))
        dateAcquisition = check_is_date_not_required('dateAcquisition', data.get('dateAcquisition'), errors)
        status_land = check_if_select_return_string('statut_land', data.get('statut_land'), errors)
        notes = checkIfStringNotRequired(data.get('description'))
        if not errors:
            id_current_user = owner if current_user.role == 'Admin' else current_user.id 
            PlotLand.objects.create(oipah=current_user.oipah, owner_land_id=id_current_user, statut_land=status_land,
                                    filiere_id=filiere, area=superficie, department=departement, sub_prefecture=sousPrefecture,
                                    quater=village, gps=gps, land_ownership=tenureFonciere, acd_number=titreFoncier,
                                    type_ground=typeSol, source_water=sourceEau, date_owner=dateAcquisition, description=notes)
            return Response({'result':True}, status=status.HTTP_201_CREATED)
        else:
            return Response({'errors':errors}, status=status.HTTP_400_BAD_REQUEST)
        

class PlotLandEditAPIView(APIView):
    permission_classes = [IsAuthenticated]
    
    def put(self, request, id_land):
        current_user = request.user
        errors = {}
        try:
            land = PlotLand.objects.get(id=int(id_land), oipah=current_user.oipah)
        except PlotLand.DoesNotExist:
            errors['land'] = "Cette parcelle n'existe pas."
        data = request.data
        errors = {}
        c = PlotLand.objects.filter(oipah=current_user.oipah)
        if current_user.role == 'Admin':
            owner = check_if_select_return_string('owner_land', data.get('owner_land'), errors)
        departement = checkIfStringRequired('department', data.get('department'), errors)
        sousPrefecture = checkIfStringRequired('sub_prefecture', data.get('sub_prefecture'), errors)
        village = checkIfStringRequired('quater', data.get('quater'), errors)
        gps = checkIfStringNotRequired(data.get('gps'))
        superficie = check_int_or_float('area', data.get('area'), errors)
        filiere = check_if_select_return_string('filiere', data.get('filiere'), errors)
        typeSol = check_if_select_return_string('type_ground', data.get('type_ground'), errors)
        sourceEau = check_if_select_return_string('source_water', data.get('source_water'), errors)
        tenureFonciere = check_if_select_return_string('land_ownership', data.get('land_ownership'), errors)
        titreFoncier = checkIfStringNotRequired(data.get('acd_number'))
        dateAcquisition = check_is_date_not_required('dateAcquisition', data.get('dateAcquisition'), errors)
        status_land = check_if_select_return_string('statut_land', data.get('statut_land'), errors)
        notes = checkIfStringNotRequired(data.get('description'))
        if not errors:
            id_current_user = owner if current_user.role == 'Admin' else current_user.id
            land.owner_land_id = int(id_current_user)
            land.statut_land = status_land
            land.filiere_id = filiere
            land.area = superficie
            land.department = departement
            land.sub_prefecture = sousPrefecture
            land.quater = village
            land.gps = gps
            land.land_ownership = tenureFonciere
            land.acd_number = titreFoncier
            land.type_ground = typeSol
            land.source_water = sourceEau
            land.date_owner = dateAcquisition
            land.description = notes
            land.save()
            return Response({'result':True}, status=status.HTTP_201_CREATED)
        else:
            return Response({'errors':errors}, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, id_land):
        current_user = request.user
        errors = {}
        try:
            land = PlotLand.objects.get(id=int(id_land), oipah=current_user.oipah)
        except PlotLand.DoesNotExist:
            errors['land'] = "Cette parcelle n'existe pas."
        if land:
            land.delete()
        return Response({"result":True}, status=status.HTTP_200_OK)
        
        
