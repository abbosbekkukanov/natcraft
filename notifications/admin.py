from django.contrib import admin
from django.core.mail import send_mail
from django.conf import settings
from .models import Notification, UserNotification
from django.contrib.auth import get_user_model
import logging

User = get_user_model()
logger = logging.getLogger(__name__)

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('title', 'target', 'created_at', 'is_sent')
    list_filter = ('target', 'is_sent')
    search_fields = ('title', 'message')

    actions = ['send_notification']

    def send_notification(self, request, queryset):
        logger.info(f"Starting send_notification for {queryset.count()} notifications")
        for notification in queryset:
            if not notification.is_sent:
                logger.info(f"Processing notification: {notification.title}, Target: {notification.target}")
                if notification.target == 'all':
                    users = User.objects.all()
                elif notification.target == 'sellers':
                    users = User.objects.filter(is_verified=True)
                else:  # buyers
                    users = User.objects.filter(is_verified=False)

                logger.info(f"Found {users.count()} users to notify")
                if not users.exists():
                    logger.warning("No users found for this target!")
                    self.message_user(request, "Hech qanday foydalanuvchi topilmadi!", level='warning')
                    return

                for user in users:
                    UserNotification.objects.get_or_create(
                        user=user,
                        notification=notification
                    )
                    logger.info(f"Sending email to {user.email}")
                    try:
                        send_mail(
                            subject=notification.title,
                            message=notification.message,
                            from_email=settings.EMAIL_HOST_USER,
                            recipient_list=[user.email],
                            fail_silently=False,
                        )
                        logger.info(f"Email successfully sent to {user.email}")
                    except Exception as e:
                        logger.error(f"Failed to send email to {user.email}: {str(e)}")
                        self.message_user(request, f"Email yuborishda xato: {str(e)}", level='error')
                        return

                notification.is_sent = True
                notification.save()
                logger.info(f"Notification {notification.title} marked as sent")
        self.message_user(request, "Bildirishnomalar muvaffaqiyatli yuborildi va emaillarga jo‘natildi!")

    send_notification.short_description = "Tanlangan bildirishnomalarni yuborish va emailga jo‘natish"

@admin.register(UserNotification)
class UserNotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'notification', 'is_read', 'received_at')
    list_filter = ('is_read',)
    search_fields = ('user__email', 'notification__title')