from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
import random
import string
# Custom User Manager
class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email field is required')
        email = self.normalize_email(email)
        extra_fields.setdefault('is_active', False)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True) 
        
        return self.create_user(email, password, **extra_fields)

# Custom User Model
class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=40, blank=True, null=True)
    last_name = models.CharField(max_length=40, blank=True, null=True) 
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name']

    def __str__(self):
        return self.email

# UserProfile Model
class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(null=True, blank=True)
    profile_image = models.ImageField(upload_to='profile_images/', null=True, blank=True)
    address = models.CharField(max_length=255, null=True, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    phone_number = models.CharField(max_length=20, null=True, blank=True)

    def __str__(self):
        return f"{self.user.email}'s profile"

class EmailConfirmation(models.Model):
    email = models.EmailField(unique=True)
    confirmation_code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True) 
    is_confirmed = models.BooleanField(default=False)

    def generate_confirmation_code(self):
        if self.is_confirmed:
            raise ValueError("Confirmation code already used.")
        self.confirmation_code = ''.join(random.choices(string.digits, k=6))
        self.save(update_fields=['confirmation_code'])

    def is_code_valid(self):
        return (timezone.now() - self.created_at) < timedelta(minutes=5)

    def __str__(self):
        return self.email

from django.utils.timezone import now
from django.contrib.auth import get_user_model

User = get_user_model()

@receiver(post_save, sender=EmailConfirmation)
def delete_expired_email_codes(sender, instance, **kwargs):
    EmailConfirmation.objects.filter(created_at__lt=now() - timedelta(minutes=5), is_confirmed=False).delete()

class PasswordResetCode(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_valid(self):
        return (now() - self.created_at).seconds < 300

@receiver(post_save, sender=PasswordResetCode)
def delete_expired_password_reset_codes(sender, instance, **kwargs):
    PasswordResetCode.objects.filter(created_at__lt=now() - timedelta(minutes=5)).delete()

