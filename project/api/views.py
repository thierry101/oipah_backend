from decimal import Decimal

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction

from authentication.permissions import AdminPermissions
from backend.regex import check_amount, check_if_select_return_string, check_is_date_required, check_multi_select_list_required, checkIfStringNotRequired, checkIfStringRequired
from backend.utils.custom_pagination import CustomPagination
from grantors.models import Subsidy
from project.api.serializers import HistorikProjectOtherSerializer, ProjectModelSerializer
from project.models import HistorikProject, ProjectModel, ProjectSubsidy


class ProjectAPIView(APIView):
    permission_classes = [AdminPermissions]
    
    def get(self, request):
        current_user = request.user
        paginator = CustomPagination()
        search = request.GET.get('search', '').strip()
        print("the search is ", search)
        projects = ProjectModel.objects.filter(oipah=current_user.oipah).order_by('-created_at')
        if search:
            projects = projects.filter(name__icontains=search)
        result_page = paginator.paginate_queryset(projects, request)
        serializer = ProjectModelSerializer( result_page, many=True)
        response = paginator.get_paginated_response(serializer.data)
        others = {"nber_project": projects.count()}
        response.data['other_params'] = others
        return response
    
    @transaction.atomic
    def post(self, request):
        current_user = request.user
        data = request.data
        errors = {}

        title = checkIfStringRequired('name', data.get('name'), errors)
        filiere_id = check_multi_select_list_required('filiere', data.get('filiere'), errors)
        typeProjet = check_if_select_return_string('type_project', data.get('type_project'), errors)
        modeExecution = check_if_select_return_string('modeExecution', data.get('modeExecution'), errors)
        plotLand_id = check_if_select_return_string('plot_land', data.get('plot_land'), errors)
        subsidy_ids = check_multi_select_list_required('subsidies', data.get('subsidies'), errors)
        dateSoumission = check_is_date_required('submission_date', data.get('submission_date'), errors)
        dateDemarrage = check_is_date_required('start_date', data.get('start_date'), errors)
        dateFin = check_is_date_required('end_date', data.get('end_date'), errors)
        description = checkIfStringNotRequired(data.get('description'))
        objectifs = checkIfStringNotRequired(data.get('purpose'))
        status_project = check_if_select_return_string('current_statut', data.get('current_statut'), errors)
        budget = Decimal(str(check_amount('budget', data.get('budget'), errors) or 0))
        cost_per_ha = check_amount('cost_per_ha', data.get('cost_per_ha'), errors)
        duree = data.get('nber_days', 0)

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
            type_project=typeProjet, current_statut=status_project, plot_land_id=plotLand_id.get('id'), budget=budget,
            cost_per_ha=cost_per_ha, submission_date=dateSoumission, start_date=dateDemarrage, end_date=dateFin,
            description=description, nber_days=duree, purpose=objectifs)
        project.filiere.set(filiere_id)
        HistorikProject.objects.create(project=project, statut_project=status_project, message=description)
        budget_remaining = budget

        for subsidy in subsidies_queryset:
            available = subsidy.dynamic_amount or Decimal('0.00')
            if budget_remaining <= Decimal('0.00'):
                break
            amount_before = available
            # montant utilisé
            if available >= budget_remaining:
                amount_used = budget_remaining
                subsidy.dynamic_amount = available - budget_remaining
                budget_remaining = Decimal('0.00')
            else:
                amount_used = available
                budget_remaining -= available
                subsidy.dynamic_amount = Decimal('0.00')
            amount_after = subsidy.dynamic_amount
            subsidy.save()
            # historique
            ProjectSubsidy.objects.create(project=project, subsidy=subsidy, amount_used=amount_used,
                amount_before=amount_before, amount_after=amount_after)
        return Response({'result': "ok"}, status=status.HTTP_200_OK)
            

class ProjectDetailAPIView(APIView):
    permission_classes = [AdminPermissions]
    
    def get(self, request, id_project):
        historik = HistorikProject.objects.filter(project_id=int(id_project))
        serializer = HistorikProjectOtherSerializer(historik, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def put(self, request, id_project):
        data = request.data
        current_statut = data.get('newStatut')
        message = data.get('message')
        try:
            project = ProjectModel.objects.get(id=id_project, oipah=request.user.oipah)
        except ProjectModel.DoesNotExist:
            return Response({'error': 'Projet non trouvé.'}, status=status.HTTP_404_NOT_FOUND)
        if project:
            project.current_statut = current_statut
            project.save()
            HistorikProject.objects.create(project=project, statut_project=current_statut, message=message)
        return Response({'result': "ok"}, status=status.HTTP_200_OK)
    
    @transaction.atomic
    def delete(self, request, id_project):
        current_user = request.user
        pro_subsidies = ProjectSubsidy.objects.filter(project_id=id_project)
        for p_sub in pro_subsidies:
            subsidy = p_sub.subsidy
            subsidy.dynamic_amount = (subsidy.dynamic_amount or Decimal('0.00')) + (p_sub.amount_used or Decimal('0.00'))
            subsidy.save()
        pro_subsidies.delete()
        ProjectModel.objects.filter(id=id_project, oipah=current_user.oipah).first().delete()
        HistorikProject.objects.filter(project_id=id_project).delete()
        return Response({'result': "ok"}, status=status.HTTP_200_OK)
        