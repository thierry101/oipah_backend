from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from backend.regex import check_if_select_return_string, check_int_or_float, check_is_date_not_required, checkIfStringNotRequired, checkIfStringRequired, get_unique_name
from plotLand.models import PlotLand



class PlotLandAPIView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        pass
    
    def post(self, request):
        current_user = request.user
        data = request.data
        errors = {}
        lands = PlotLand.objects.filter(oipah=current_user.oipah)
        code_land = get_unique_name('code', lands, data.get('code'), errors, 'code_land')
        if current_user.role == 'Admin':
            owner = check_if_select_return_string('owner', data.get('owner'), errors)
        departement = checkIfStringRequired('departement', data.get('departement'), errors)
        sousPrefecture = checkIfStringRequired('sousPrefecture', data.get('sousPrefecture'), errors)
        village = checkIfStringRequired('village', data.get('village'), errors)
        gps = checkIfStringNotRequired(data.get('gps'))
        filiere = check_if_select_return_string('filiere', data.get('filiere'), errors)
        typeSol = check_if_select_return_string('typeSol', data.get('typeSol'), errors)
        sourceEau = check_if_select_return_string('sourceEau', data.get('sourceEau'), errors)
        tenureFonciere = check_if_select_return_string('tenureFonciere', data.get('tenureFonciere'), errors)
        titreFoncier = checkIfStringNotRequired(data.get('titreFoncier'))
        dateAcquisition = check_is_date_not_required('dateAcquisition', data.get('dateAcquisition'), errors)
        status_land = check_if_select_return_string('status', data.get('status'), errors)
        notes = checkIfStringNotRequired(data.get('notes'))
        superficie = check_int_or_float('superficie', data.get('superficie'), errors)
        if not errors:
            id_current_user = owner if current_user.role == 'Admin' else current_user.id 
            PlotLand.objects.create(oipah=current_user.oipah, owner_land_id=id_current_user, code_land=code_land, statut_land=status_land,
                                    filiere_id=filiere, area=superficie, department=departement, sub_prefecture=sousPrefecture,
                                    quater=village, gps=gps, land_ownership=tenureFonciere, acd_number=titreFoncier,
                                    type_ground=typeSol, source_water=sourceEau, date_owner=dateAcquisition, description=notes)
            return Response({'result':True}, status=status.HTTP_201_CREATED)
        else:
            return Response({'errors':errors}, status=status.HTTP_400_BAD_REQUEST)
