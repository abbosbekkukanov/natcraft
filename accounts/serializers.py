from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import EmailConfirmation, PasswordResetCode
from django.core.mail import send_mail
from django.conf import settings 
import random
import string

import logging
logger = logging.getLogger(__name__)

User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ('first_name', 'email', 'password')

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("This email is already registered.")
        return value
    
    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        
        confirmation = EmailConfirmation.objects.create(email=user.email)
        confirmation.generate_confirmation_code()
        send_mail(
            "Email Confirmation",
            f"Your confirmation code is: {confirmation.confirmation_code}",
            settings.EMAIL_HOST_USER,
            [user.email]
        )   
        
        return user

class EmailConfirmationSerializer(serializers.Serializer):
    email = serializers.EmailField()
    confirmation_code = serializers.CharField(max_length=6)

    def validate(self, data):
        email = data.get('email')
        code = data.get('confirmation_code')
        print("Email:", email, "Code:", code, "<----------- 42 line")
        try:
            confirmation = EmailConfirmation.objects.get(email=email)
        except EmailConfirmation.DoesNotExist:
            raise serializers.ValidationError("Email confirmation not found.")

        if confirmation.is_confirmed:
            raise serializers.ValidationError("This email is already confirmed.")
        
        if not confirmation.is_code_valid():
            raise serializers.ValidationError("Confirmation code has expired.")

        if confirmation.confirmation_code != code:
            logger.debug(f"Expected code: {confirmation.confirmation_code}, Received code: {code}")
            raise serializers.ValidationError("Invalid confirmation code.")
        
        data['confirmation'] = confirmation
        return data

    def save(self):
        confirmation = self.validated_data['confirmation']
        confirmation.is_confirmed = True
        confirmation.save(update_fields=['is_confirmed'])
        
        # Foydalanuvchini faollashtiramiz:
        user = User.objects.get(email=confirmation.email)
        user.is_active = True
        user.save(update_fields=['is_active'])
        confirmation.delete() # Confirmation obyektini o'chiramiz   
        return user
    
class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        try:
            user = User.objects.get(email=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("User with this email does not exist.")
        self.context['user'] = user
        return value

    def save(self):
        user = self.context['user']
        reset_code = PasswordResetCode.objects.create(user=user, code=''.join(random.choices(string.digits, k=6)))
        # Bu yerda emailga reset code yuborish logikasi qo'shiladi
        send_mail(
            "Password Reset Code",
            f"Your password reset code is: {reset_code.code}",
            settings.EMAIL_HOST_USER,
            [user.email],
    
        )
        return reset_code
    
class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField(max_length=6)
    new_password = serializers.CharField(write_only=True)
    
    def validate(self, data):
        email = data.get('email')
        code = data.get('code')
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError("User not found.")
        
        try:
            reset_code = PasswordResetCode.objects.get(user=user, code=code)
        except PasswordResetCode.DoesNotExist:
            raise serializers.ValidationError("Invalid reset code.")
        
        if not reset_code.is_valid():
            raise serializers.ValidationError("Reset code has expired.")
        
        data['user'] = user
        data['reset_code'] = reset_code
        return data

    def save(self):
        user = self.validated_data['user']
        new_password = self.validated_data['new_password']
        user.set_password(new_password)
        user.save()
        # Agar reset kodini birdan ko'p ishlatishni oldini olish kerak bo'lsa, uni o'chirish mumkin.
        self.validated_data['reset_code'].delete()
        return user
