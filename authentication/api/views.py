from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.contrib.auth import authenticate
from django.db import transaction
from django.db.models import Q
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken, TokenError


from authentication.api.serializers import UserMiniSerializer, UserSerializer
from authentication.models import User
from authentication.permissions import AdminPermissions
from backend.regex import check_if_select_return_string, check_phone_numberRequired, checkIfEmailRequiredForRegisterFirstTime, checkIfStringNotRequired, checkIfStringRequired, checkIfUserAgree, passwordCheckRequired
from backend.utils.custom_pagination import CustomPagination
from oipah.models import OipahAttribute



class RegisterUserAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        data = request.data
        errors = {}
        name = checkIfStringNotRequired(data.get('name'))
        surname = checkIfStringNotRequired(data.get('surname'))
        oipah = checkIfStringRequired("oipahName", data.get('oipahName'), errors)
        email = checkIfEmailRequiredForRegisterFirstTime('email', data.get('email'), User, errors)
        password = passwordCheckRequired("password", data.get('password'), 8, errors)
        phone = check_phone_numberRequired('phone', data.get('phone'), errors)
        acceptTerms = checkIfUserAgree('acceptTerms', data.get('acceptTerms'), errors)
        if errors:
            return Response({'errors':errors}, status=status.HTTP_400_BAD_REQUEST)
        else:
            user = User.objects.create(name=name, surname=surname, email=email, phone=phone, role='Admin', acceptTerms=acceptTerms, is_verified=True)
            user.set_password(password)
            oipah = OipahAttribute.objects.create(name=oipah, phone=phone, email=email)
            user.oipah = oipah
            user.save()
        return Response("success", status=status.HTTP_201_CREATED)
    

class RegisterUserByAdmin(APIView):
    permission_classes = [AdminPermissions]
    
    def get(self, request):

        user = request.user
        search = request.GET.get('search', '').strip()

        users = User.objects.filter(oipah=user.oipah).order_by('-date_joined', '-last_seen')
        if search:
                users = users.filter(Q(name__icontains=search) | Q(surname__icontains=search) | Q(email__icontains=search))
        paginator = CustomPagination()
        result_page = paginator.paginate_queryset(users, request)
        serializer = UserMiniSerializer( result_page, many=True)
        
        return paginator.get_paginated_response( serializer.data)

    @transaction.atomic
    def post(self, request):
        user = request.user
        data = request.data
        errors = {}

        name = checkIfStringRequired('name', data.get('name'), errors)
        surname = checkIfStringRequired('surname', data.get('surname'), errors)
        email = checkIfEmailRequiredForRegisterFirstTime('email', data.get('email'), User, errors)
        phone = check_phone_numberRequired('phone', data.get('phone'), errors)
        type_doc = check_if_select_return_string('type_doc', data.get('type_doc'), errors)
        password = passwordCheckRequired('password', data.get('password'), 8, errors)
        nber_document = checkIfStringRequired('nber_doc', data.get('nber_doc'), errors)
        role = check_if_select_return_string('role', data.get('role'), errors)

        if errors:
            return Response({"errors": errors}, status=status.HTTP_400_BAD_REQUEST)

        try:
            new_user = User.objects.create(name=name, surname=surname, email=email, role=role,
                phone=phone, type_doc=type_doc, nber_doc=nber_document, oipah=user.oipah)
            new_user.set_password(password)
            new_user.save()
            return Response({'result': True}, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({'result': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class RegisterUserDetailAPIView(APIView):
    permission_classes = [AdminPermissions]
    
    @transaction.atomic
    def put(self, request, id_user):
        current_user = request.user
        datas = request.data
        errors = {}
        checker = datas.get('checker')
        if checker == 'infos':
            data = datas.get('data')
            name = checkIfStringRequired('name', data.get('name'), errors)
            surname = checkIfStringRequired('surname', data.get('surname'), errors)
            phone = check_phone_numberRequired('phone', data.get('phone'), errors)
            type_doc = check_if_select_return_string('type_doc', data.get('type_doc'), errors)
            nber_document = checkIfStringRequired('nber_doc', data.get('nber_doc'), errors)
            role = check_if_select_return_string('role', data.get('role'), errors)
            try:
                user = User.objects.get(oipah=current_user.oipah, id=id_user)
            except User.DoesNotExist:
                errors['user'] = "Cet utilisateur n'existe pas"
            if not errors:
                user.name = name
                user.surname = surname
                user.phone = phone
                user.type_doc = type_doc
                user.nber_doc = nber_document
                user.role = role
                user.save()
                return Response({'result': True}, status=status.HTTP_200_OK)
            else:
                return Response({"errors": errors}, status=status.HTTP_400_BAD_REQUEST)
        if checker == 'password':
            password = passwordCheckRequired('password', datas.get('password'), 8, errors)
            if not errors:
                user = User.objects.get(oipah=current_user.oipah, id=id_user)
                user.set_password(password)
                user.save()
                return Response({'result': True}, status=status.HTTP_200_OK)
            else:
                return Response({"errors": errors}, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, id_user):
        current_user = request.user
        try:
            user = User.objects.get(oipah=current_user.oipah, id=id_user)
        except User.DoesNotExist:
            pass
        if user:
            user.delete()
            return Response({'result': True}, status=status.HTTP_200_OK)


class LoginUserViewAPIView(APIView):
    
    @transaction.atomic
    def post(self, request):
        errors = {}
        data = request.data
        email = data.get('email')
        password = data.get('password')

        # 1. Authentification
        user = authenticate(email=email, password=password)

        # 2. Vérifications de sécurité
        if not user:
            errors["login"] = "Email ou mot de passe incorrect"
        elif not user.is_verified:
            errors["login"] = "Email non vérifié"
        elif not user.is_active:
            errors["login"] = "Compte désactivé, contactez votre administrateur"

        # 3. Réponse
        if not errors:
            # On utilise ta méthode .tokens() définie sur ton modèle User
            user_tokens = user.tokens()
            
            return Response({
                "access_token": str(user_tokens['access']),
                "refresh_token": str(user_tokens['refresh'])
            }, status=status.HTTP_200_OK)
        
        else:
            return Response({"errors": errors}, status=status.HTTP_400_BAD_REQUEST)
        

class LogoutAPIView(APIView):
    permission_classes = [IsAuthenticated]
    
    @transaction.atomic
    def post(self, request):
        errors = {}
        self.token = request.user.tokens()['refresh']
        try:
            token = RefreshToken(self.token)
            token.blacklist()
            return Response({'result':True}, status=status.HTTP_204_NO_CONTENT)
        except TokenError:
            errors["token"] = "Token non valide ou expiré"
            return Response({'result':errors}, status=status.HTTP_400_BAD_REQUEST)
            

class StateUserView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        serial = UserSerializer(user)
        return Response(serial.data, status=status.HTTP_200_OK)


