from decimal import Decimal

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction

from authentication.permissions import AdminPermissions
from backend.regex import check_amount, check_if_select_return_string, check_is_date_required, check_multi_select_list_required, checkIfStringNotRequired, checkIfStringRequired
from backend.utils.custom_pagination import CustomPagination
from grantors.models import Subsidy
from project.api.serializers import ProjectModelSerializer
from project.models import ProjectModel


class ProjectAPIView(APIView):
    permission_classes = [AdminPermissions]
    
    
    def get(self, request):
        current_user = request.user
        paginator = CustomPagination()
        projects = ProjectModel.objects.filter(oipah=current_user.oipah).order_by('-created_at')
        result_page = paginator.paginate_queryset(projects, request)
        serializer = ProjectModelSerializer( result_page, many=True)
        response = paginator.get_paginated_response(serializer.data)
        # response.data['other_params'] = others
        return response
        
    
    @transaction.atomic
    def post(self, request):
        current_user = request.user
        data = request.data
        errors = {}

        title = checkIfStringRequired('titre', data.get('titre'), errors)
        filiere_id = check_if_select_return_string('filiere', data.get('filiere'), errors)
        typeProjet = check_if_select_return_string('typeProjet', data.get('typeProjet'), errors)
        modeExecution = check_if_select_return_string('modeExecution', data.get('modeExecution'), errors)
        plotLand_id = check_if_select_return_string('plotLand', data.get('plotLand'), errors)

        subsidy_ids = check_multi_select_list_required('subsidies', data.get('subsidies'), errors)

        dateSoumission = check_is_date_required('dateSoumission', data.get('dateSoumission'), errors)
        dateDemarrage = check_is_date_required('dateDemarrage', data.get('dateDemarrage'), errors)
        dateFin = check_is_date_required('dateFin', data.get('dateFin'), errors)

        description = checkIfStringNotRequired(data.get('description'))
        objectifs = checkIfStringNotRequired(data.get('objectifs'))

        status_project = check_if_select_return_string('status', data.get('status'), errors)

        budget = Decimal(str(check_amount('budget', data.get('budget'), errors) or 0))
        cost_per_ha = check_amount('cost_per_ha', data.get('cost_per_ha'), errors)

        duree = data.get('duree', 0)

        subsidies_queryset = Subsidy.objects.none()
        total_available = Decimal('0.00')

        if subsidy_ids:
            subsidies_queryset = Subsidy.objects.filter(id__in=subsidy_ids, dynamic_amount__gt=0).order_by('dynamic_amount')

            total_available = sum((s.dynamic_amount or Decimal('0.00')) for s in subsidies_queryset)

        if subsidies_queryset and total_available < budget:
            errors['subsidies'] = "Les subventions disponibles sont insuffisantes."

        if errors:
            return Response({'errors': errors}, status=status.HTTP_400_BAD_REQUEST)

        project = ProjectModel.objects.create(oipah=current_user.oipah, name=title, modeExecution=modeExecution,
            type_project=typeProjet, current_statut=status_project, plot_land_id=plotLand_id, budget=budget,
            cost_per_ha=cost_per_ha, submission_date=dateSoumission, start_date=dateDemarrage, end_date=dateFin,
            description=description, nber_days=duree, purpose=objectifs)
        project.filiere.set(filiere_id)
        budget_remaining = budget
        used_subsidies = []

        for subsidy in subsidies_queryset:

            available = subsidy.dynamic_amount or Decimal('0.00')

            if budget_remaining <= Decimal('0.00'):
                break

            used_subsidies.append(subsidy)

            if available >= budget_remaining:
                subsidy.dynamic_amount = available - budget_remaining
                budget_remaining = Decimal('0.00')
            else:
                budget_remaining -= available
                subsidy.dynamic_amount = Decimal('0.00')

            subsidy.save()
            
        project.subsidies.set(used_subsidies)
        return Response({'result': "ok"}, status=status.HTTP_200_OK)
            
            