from django.contrib.auth import get_user_model, authenticate
from django.core.mail import send_mail
from django.conf import settings 
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import EmailConfirmation, PasswordResetCode, UserProfile, Profession
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
        user = User.objects.filter(email=value).first()

        if user:
            if user.is_active:
                raise serializers.ValidationError("This email is already registered and verified.")
            else:
                # Agar email tasdiqlanmagan bo‘lsa, tasdiqlash kodini qayta yuboramiz.
                confirmation, created = EmailConfirmation.objects.get_or_create(email=value)
                confirmation.generate_confirmation_code()
                
                send_mail(
                    "Email Confirmation",
                    f"Your new confirmation code is: {confirmation.confirmation_code}",
                    settings.EMAIL_HOST_USER,
                    [value]
                )

                raise serializers.ValidationError(
                    "This email is already registered but not verified. A new confirmation code has been sent."
                )

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
        try:
            confirmation = EmailConfirmation.objects.get(email=email)
        except EmailConfirmation.DoesNotExist:
            raise serializers.ValidationError("Email confirmation not found.")

        if confirmation.is_confirmed:
            raise serializers.ValidationError("This email is already confirmed.")
        
        if not confirmation.is_code_valid():
            raise serializers.ValidationError("Confirmation code has expired.")

        if confirmation.confirmation_code != code:
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
        confirmation.delete()
        return user

# Token olish uchun serializer Login
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer): 
    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        user = authenticate(username=email, password=password)
        if not user:
            raise serializers.ValidationError({"detail": "Incorrect email or password."})

        if not user.is_active:
            raise serializers.ValidationError({"detail": "Your account is not verified. Please check your email."})

        return super().validate(attrs)
    
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
    

class PasswordResetVerifySerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField(max_length=6)

    def validate(self, data):
        email = data.get('email')
        code = data.get('code')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError({"email": "User with this email does not exist."})

        try:
            reset_code = PasswordResetCode.objects.get(user=user, code=code)
        except PasswordResetCode.DoesNotExist:
            raise serializers.ValidationError({"code": "Invalid reset code."})

        if not reset_code.is_valid():
            raise serializers.ValidationError({"code": "Reset code has expired."})

        data['user'] = user
        data['reset_code'] = reset_code
        return data


class PasswordResetConfirmSerializer(serializers.Serializer):
    email = serializers.EmailField()
    new_password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get('email')
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError({"email": "User with this email does not exist."})

        data['user'] = user
        return data

    def save(self):
        user = self.validated_data['user']
        new_password = self.validated_data['new_password']
        user.set_password(new_password)
        user.save()

        PasswordResetCode.objects.filter(user=user).delete()
        return user

class ProfessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profession
        fields = ['id', 'name']


class UserProfileSerializer(serializers.ModelSerializer):
    user_email = serializers.ReadOnlyField(source='user.email')
    user_first_name = serializers.CharField(source='user.first_name')
    is_verified = serializers.BooleanField(source='user.is_verified', read_only=True)
    profession = ProfessionSerializer()

    class Meta:
        model = UserProfile
        fields = "__all__"
        read_only_fields = ['id', 'user_email', 'created_at', 'updated_at']
        ref_name = 'AccountsUserProfile'

    def create(self, validated_data):
        user_data = validated_data.pop('user', None)
        if user_data and 'first_name' in user_data:
            user = self.context['request'].user
            user.first_name = user_data['first_name']
            user.save()
        
        profile = UserProfile.objects.create(user=self.context['request'].user, **validated_data)
        return profile

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', None)
        if user_data and 'first_name' in user_data:
            instance.user.first_name = user_data['first_name']
            instance.user.save()

        profession_id = self.context['request'].data.get('profession')
        if profession_id:
            try:
                profession = Profession.objects.get(id=profession_id)
                validated_data['profession'] = profession
            except Profession.DoesNotExist:
                logger.error(f"Profession with id {profession_id} not found")
                raise serializers.ValidationError({"profession": f"Profession with id {profession_id} not found"})
            
        for attr, value in validated_data.items():
            setattr(instance, attr, value if value != "" else None)
        instance.save()
        return instance

    def validate_phone_number(self, value):
        if not value:
            raise serializers.ValidationError("Phone number is required!")
        return value

    def validate_profession(self, value):
        if not value:
            raise serializers.ValidationError("Profession is required!")
        return value

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['profession'] = instance.profession_id
        return representation
    
