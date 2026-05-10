from rest_framework import permissions
from authentication.api.serializers import UserSerializer


class RootPermissions(permissions.BasePermission): #Super Administrateur de l'application
    def has_permission(self, request, view):
        data = UserSerializer(request.user).data
        root = data['role'] == 'Root'
        if request.method == 'POST' or request.method == 'PUT' or request.method == 'GET' or request.method == 'DELETE':
            return root

        
class AdminPermissions(permissions.BasePermission): #Administrateur de l'application
    def has_permission(self, request, view):
        data = UserSerializer(request.user).data
        admin = data['role'] == 'Admin'
        if request.method == 'POST' or request.method == 'PUT' or request.method == 'GET' or request.method == 'DELETE':
            return admin

        
class AgriculturalPermissions(permissions.BasePermission): #Entrepreneur agricole
    def has_permission(self, request, view):
        data = UserSerializer(request.user).data
        siteAdmin = data['role'] == 'Agricultural'
        if request.method == 'POST' or request.method == 'PUT' or request.method == 'GET' or request.method == 'DELETE':
            return siteAdmin


class DafPermissions(permissions.BasePermission): #Comptable
    def has_permission(self, request, view):
        data = UserSerializer(request.user).data
        validator = data['role'] == 'Daf'
        if request.method == 'POST' or request.method == 'PUT' or request.method == 'GET' or request.method == 'DELETE':
            return validator
                        
                        