from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.base_user import BaseUserManager
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django_resized import ResizedImageField

from rest_framework_simplejwt.tokens import RefreshToken
from oipah.models import OipahAttribute


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError(_('The Email must be set'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_verified', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    username = None
    oipah = models.ForeignKey(OipahAttribute, on_delete=models.CASCADE, blank=True, null=True)
    name = models.CharField(max_length=100, blank=True, null=True)
    surname = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(unique=True, blank=True, null=True)
    phone = models.CharField(max_length=50, blank=True, null=True)
    role = models.CharField(max_length=20, blank=True, null=True)
    type_doc = models.CharField(max_length=20, blank=True, null=True)
    nber_doc = models.CharField(max_length=20, blank=True, null=True)
    image = ResizedImageField(upload_to='Photos de profil', blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    acceptTerms = models.BooleanField(null=True, blank=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now=True)
    last_seen = models.DateTimeField(null=True, blank=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    
    def tokens(self):
        refresh = RefreshToken.for_user(self)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token)
        }


    objects = CustomUserManager()
    class Meta:
        # ordering = ['-last_login']
        verbose_name_plural = 'utilisateurs'
        
    

class Permission(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True) #si je met SET_NULL, la suppression de l'utilisateur ne supprime pas le permission
    oipah = models.ForeignKey(OipahAttribute, on_delete=models.CASCADE, blank=True, null=True)
    content_type = models.CharField(max_length=100, blank=True, null=True)  # permet de savoir sur quel model appliquer la permission e.g., 'book', 'author'
    object_id = models.PositiveIntegerField(null=True, blank=True)  # null means permission for all objects of that type Si on spécifie un object_id, la permission sera appliquée uniquement sur cet objet dans la table
    permission_type = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    class Meta:
        verbose_name_plural = 'permissions'
        ordering = ['-updated']
        unique_together = ("user", "content_type", "object_id", "permission_type")


class OneTimePassword(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='otps')
    otp = models.CharField(max_length=128)  # HASHER
    attempts = models.PositiveSmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    expired_at = models.DateTimeField(db_index=True, blank=True, null=True)
    is_used = models.BooleanField(default=False)
    
    class Meta:
        indexes = [
            models.Index(fields=['user', 'is_used']),
            models.Index(fields=['expired_at']),
        ]

    def is_expired(self):
        return timezone.now() >= self.expired_at
    


    
