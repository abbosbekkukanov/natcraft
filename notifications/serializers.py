from rest_framework import serializers
from .models import Notification, UserNotification

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'title', 'message', 'created_at']

class UserNotificationSerializer(serializers.ModelSerializer):
    notification = NotificationSerializer(read_only=True)

    class Meta:
        model = UserNotification
        fields = ['id', 'user', 'notification', 'is_read', 'received_at']
        read_only_fields = ['user', 'notification', 'received_at']