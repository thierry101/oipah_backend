from decimal import Decimal

from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Q
from rest_framework import status
from django.db import transaction
from django.core.exceptions import ValidationError

from authentication.models import User
from authentication.permissions import AdminPermissions
from backend.regex import check_amount, check_if_select_return_string, check_int_or_float, check_is_date_required, check_multi_select_list_required, checkIfStringNotRequired, checkIfStringRequired
from backend.utils.custom_pagination import CustomPagination
from grantors.models import Subsidy
from project.api.serializers import CommissionProjectOtherSerializer, HistorikProjectOtherSerializer, ProjectChargeSerializer, ProjectModelSerializer, UserSerializerMini
from project.models import CommissionProject, HistorikProject, ProjectCharge, ProjectModel, ProjectProducts, ProjectSubsidy


class ProjectAPIView(APIView):
    permission_classes = [AdminPermissions]
    
    def get(self, request):
        current_user = request.user
        paginator = CustomPagination()
        search = request.GET.get('search', '').strip()
        statut_land = request.GET.get('statut_land', '').strip()
        filiere = request.GET.get('filiere', '').strip()
        type_project = request.GET.get('type_project', '').strip()
        projects = ProjectModel.objects.filter(oipah=current_user.oipah).order_by('-created_at')
        if search:
            projects = projects.filter(name__icontains=search)
        if statut_land:
            projects = projects.filter(current_statut=statut_land)
        if filiere:
            projects = projects.filter(filiere__name=filiere)
        if type_project:
            projects = projects.filter(type_project=type_project)
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
        qty = check_int_or_float('qty', data.get('qty'), errors)
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
            description=description, nber_days=duree, purpose=objectifs, qty=qty)
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
        
        
class SettingCommissionAPIView(APIView):
    permission_classes = [AdminPermissions]
    
    def get(self, request):
        current_user = request.user
        commissions = CommissionProject.objects.filter(oipah=current_user.oipah).order_by('-created_at')
        serializer = CommissionProjectOtherSerializer(commissions, many=True)
        return Response({'result':serializer.data}, status=status.HTTP_200_OK)
    
    def post(self, request):
        current_user = request.user
        data = request.data
        errors = {}

        title = checkIfStringRequired('title', data.get('title'), errors)
        rate = check_int_or_float('rate', data.get('rate'), errors)
        is_entrepreneur = data.get('is_entrepreneur', False)

        # Erreurs des validations manuelles
        if errors:
            return Response({'errors': errors}, status=status.HTTP_400_BAD_REQUEST)
        try:
            # Enregistrement
            commission = CommissionProject(oipah=current_user.oipah, title=title, rate=rate, is_entrepreneur=is_entrepreneur)
            commission.full_clean()
            commission.save()
            serializer = CommissionProjectOtherSerializer(commission)
            return Response({'result': serializer.data}, status=status.HTTP_200_OK)

        except ValidationError as e:
            return Response({'errors': e.message_dict}, status=status.HTTP_400_BAD_REQUEST)
        

class SettingCommissionDetailAPIView(APIView):
    permission_classes = [AdminPermissions]
    
    def put(self, request, id_commission):
        current_user = request.user
        data = request.data
        errors = {}
        commission = CommissionProject.objects.filter(id=int(id_commission), oipah=current_user.oipah).first()

        title = checkIfStringRequired('title', data.get('title'), errors)
        rate = check_int_or_float('rate', data.get('rate'), errors)
        is_entrepreneur = data.get('is_entrepreneur', False)

        # Vérifications manuelles
        if title != commission.title:

            title_exists = CommissionProject.objects.filter(oipah=current_user.oipah, title__icontains=title).exclude(id=commission.id).exists()

            if title_exists:
                errors['title'] = "Une commission avec ce titre existe déjà."

        # Erreurs validations manuelles
        if errors:
            return Response({'errors': errors}, status=status.HTTP_400_BAD_REQUEST)
        try:
            # Mise à jour
            commission.title = title
            commission.rate = rate
            commission.is_entrepreneur = is_entrepreneur
            commission.full_clean()
            commission.save()
            serializer = CommissionProjectOtherSerializer(commission)
            return Response({'result':serializer.data}, status=status.HTTP_200_OK)
        except ValidationError as e:
            return Response({'errors': e.message_dict}, status=status.HTTP_400_BAD_REQUEST)
    
        
class GetEndedProjectAPIView(APIView): #liste des projets terminés
    permission_classes = [AdminPermissions]
    
    def get(self, request):
        current_user = request.user
        paginator = CustomPagination()
        search = request.GET.get('search', '').strip()
        projects = ProjectModel.objects.filter(oipah=current_user.oipah).order_by('-created_at')
        if search:
            projects = projects.filter(name__icontains=search)
        result_page = paginator.paginate_queryset(projects, request)
        serializer = ProjectModelSerializer( result_page, many=True)
        response = paginator.get_paginated_response(serializer.data)
        return response
    

class GetDriverAPIView(APIView): #Chauffeurs
    permission_classes = [AdminPermissions]
    
    def get(self, request):
        current_user = request.user
        drivers = User.objects.filter(oipah=current_user.oipah, role='Driver').order_by('first_name')
        serializer = UserSerializerMini(drivers, many=True)
        return Response({'result':serializer.data}, status=status.HTTP_200_OK)
    

class GetProjectUserAPIView(APIView):#Entrepreneurs agricole
    permission_classes = [AdminPermissions]
    
    def get(self, request):
        user = request.user
        search = request.GET.get('search', '').strip()
        users = User.objects.filter(oipah=user.oipah, role='Agricultural').order_by('first_name')
        if search:
                users = users.filter(Q(name__icontains=search) | Q(surname__icontains=search) | Q(email__icontains=search))
        paginator = CustomPagination()
        result_page = paginator.paginate_queryset(users, request)
        serializer = UserSerializerMini( result_page, many=True)
        return paginator.get_paginated_response( serializer.data)
    
    
class ProjectFinalizeAPIView(APIView):
    permission_classes = [AdminPermissions]
    
    def get(self, request, id_project):
        user = request.user
        charges = ProjectCharge.objects.filter(project_id=id_project)
        serializer = ProjectChargeSerializer(charges, many=True)
        try:
            project = ProjectModel.objects.get(id=id_project, oipah=user.oipah)
        except ProjectModel.DoesNotExist:
            return Response({'error': 'Projet non trouvé.'}, status=status.HTTP_404_NOT_FOUND)
        if project:
            harvest_qty = project.quantity_harvested or 0
            harvest_date = project.harverst_date or None
            vehicle_id = project.vehicle.id if project.vehicle else None
            driver_id = project.driver.id if project.driver else None
            others = {"harvest_qty": harvest_qty, "harvest_date": harvest_date, "vehicle_id": vehicle_id, "driver_id": driver_id}
            return Response({'result': serializer.data, 'others': others}, status=status.HTTP_200_OK)

    def post(self, request, id_project):
        user = request.user
        data = request.data
        checker = data.get('checker')
        try:
            project = ProjectModel.objects.get(id=id_project, oipah=user.oipah)
        except ProjectModel.DoesNotExist:
            return Response({'error': 'Projet non trouvé.'}, status=status.HTTP_404_NOT_FOUND)
        if checker == 'charge':
            errors = {}
            data_project = data.get('harvest')
            data_charge = data.get('transportCharges', [])
            quantity = check_int_or_float('quantity', data_project.get('quantity'), errors)
            harvest_date = check_is_date_required('date', data_project.get("date"), errors)
            transport_type = check_if_select_return_string('transportType', data_project.get('transportType'), errors)
            driver_name = check_if_select_return_string('driverName', data_project.get('driverName'), errors)
            if not data_charge:
                errors['transportCharges'] = "Les charges de transport et autres sont obligatoires."
            
            if project.current_statut != 'termine':
                return Response({'error': 'Le projet doit être terminé pour être finalisé.'}, status=status.HTTP_400_BAD_REQUEST)
            if errors:
                return Response({'errors': errors}, status=status.HTTP_400_BAD_REQUEST)
            else:
                ProjectCharge.objects.filter(project_id=id_project).delete()
                project.quantity_harvested = quantity
                project.harverst_date = harvest_date
                project.vehicle_id = transport_type
                project.driver_id = driver_name
                project.save()
                for charge in data_charge:
                    title = checkIfStringRequired('transportCharges', charge.get('label'), errors)
                    amount = Decimal(str(check_amount('transportCharges', charge.get('amount'), errors) or 0))
                    date_charge = check_is_date_required('transportCharges', charge.get('date'), errors)
                    if errors:
                        return Response({'errors': errors}, status=status.HTTP_400_BAD_REQUEST)
                    else:
                        ProjectCharge.objects.create(project=project, label=title, amount=amount, date=date_charge)
                return Response({'result':'serializer.data'}, status=status.HTTP_200_OK)
        if checker == 'recapSell':
            raw_amount = check_amount('raw_amount', data.get('raw_amount'), errors)
            transformed_items = data.get('transformed_items', [])
            if not transformed_items:
                pass
            if not errors:
                project.raw_amount = raw_amount
                project.save()
                if transformed_items:
                    for item in transformed_items:
                        name = checkIfStringRequired('name', item.get('name'), errors)
                        qty = check_int_or_float('qty', item.get('qty'), errors)
                        unit = checkIfStringRequired('unit', item.get('unit'), errors)
                        amount = Decimal(str(check_amount('amount', item.get('amount'), errors) or 0))
                        if errors:
                            return Response({'errors': errors}, status=status.HTTP_400_BAD_REQUEST)
                        else:
                            ProjectProducts.objects.create(project=project, name=name, qty=qty, unit=unit, amount=amount)
                return Response({'result':'serializer.data'}, status=status.HTTP_200_OK)
        
    def delete(self, request, id_project):
        #id_project c'est l'id de la charge à supprimer
        try:
            charge = ProjectCharge.objects.get(id=id_project)
        except ProjectCharge.DoesNotExist:
            return Response({'error': 'Charge non trouvée.'}, status=status.HTTP_404_NOT_FOUND)
        if charge:
            charge.delete()
            return Response({'result': "ok"}, status=status.HTTP_200_OK)
        
    