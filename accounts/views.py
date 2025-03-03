from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.views import APIView
from rest_framework import generics, status, serializers, viewsets, permissions
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import UserProfile, Profession
from .serializers import ( 
    RegisterSerializer, 
    EmailConfirmationSerializer, 
    PasswordResetRequestSerializer,
    PasswordResetVerifySerializer,
    PasswordResetConfirmSerializer, 
    CustomTokenObtainPairSerializer,
    UserProfileSerializer,
    ProfessionSerializer
)
from .permissions import IsAuthorOrReadOnly
from django.contrib.auth import get_user_model

User = get_user_model()

class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer

    def perform_create(self, serializer):
        serializer.save()

class EmailConfirmationView(generics.GenericAPIView):
    serializer_class = EmailConfirmationSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({"message": "Email confirmed successfully.", "user": user.email}, status=status.HTTP_200_OK)
    

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)

        # Agar user login qilgandan keyin profil mavjudligini tekshirmoqchi bo'lsak
        if response.status_code == 200 and "access" in response.data:
            user = User.objects.get(email=request.data.get("email"))
            if not UserProfile.objects.filter(user=user).exists():
                response.data["profile_required"] = "Siz hali profil yaratmagansiz, iltimos profil yarating!"

        return response

class PasswordResetRequestView(generics.GenericAPIView):
    serializer_class = PasswordResetRequestSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        reset_code = serializer.save()
        return Response({"message": "Password reset code sent to email."}, status=status.HTTP_200_OK)

class PasswordResetVerifyView(generics.GenericAPIView):
    serializer_class = PasswordResetVerifySerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Reset kod tasdiqlandi, foydalanuvchi yangi parolni kiritishi mumkin
        return Response({"message": "Reset code is valid. You can now set a new password."}, status=status.HTTP_200_OK)


class PasswordResetConfirmView(generics.GenericAPIView):
    serializer_class = PasswordResetConfirmSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({"message": "Your password has been successfully reset."}, status=status.HTTP_200_OK)



class LogoutView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        try:
            refresh_token = request.data.get('refresh_token')
            if not refresh_token:
                return Response({"detail": "Refresh token is required."}, status=status.HTTP_400_BAD_REQUEST)
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"message": "Logged out successfully"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
class ProfessionListView(generics.ListAPIView):
    queryset = Profession.objects.all()
    serializer_class = ProfessionSerializer

        

class UserProfileViewSet(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthorOrReadOnly]

    def get_queryset(self):
        if self.action in ['retrieve', 'update', 'partial_update', 'destroy']:
            return UserProfile.objects.filter(user=self.request.user)
        return UserProfile.objects.all()


    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.user != request.user:
            return Response({"detail": "You can only change your own profile."}, status=status.HTTP_403_FORBIDDEN)
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.user != request.user:
            return Response({"detail": "You can only delete your own profile."}, status=status.HTTP_403_FORBIDDEN)
        return super().destroy(request, *args, **kwargs)
    
class CraftsmenListView(generics.ListAPIView):
    serializer_class = UserProfileSerializer

    def get_queryset(self):
        queryset = UserProfile.objects.all().select_related('profession') 
        profession = self.request.query_params.get('profession')
        if profession:
            queryset = queryset.filter(profession__name__iexact=profession)
        return queryset