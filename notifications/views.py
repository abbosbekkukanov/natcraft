from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import UserNotification
from .serializers import UserNotificationSerializer

class UserNotificationViewSet(viewsets.ModelViewSet):
    serializer_class = UserNotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return UserNotification.objects.none()
        return UserNotification.objects.filter(user=self.request.user)

    @action(detail=True, methods=['post'])
    def mark_as_read(self, request, pk=None):
        # Bildirishnomani o‘qilgan deb belgilash
        notification = self.get_object()
        notification.is_read = True
        notification.save()
        return Response({"status": "Bildirishnoma o‘qildi"})