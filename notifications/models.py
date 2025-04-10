from django.db import models
from django.conf import settings

class Notification(models.Model):
    TARGET_CHOICES = (
        ('all', 'Hammaga'),
        ('sellers', 'Sotuvchilarga'),
        ('buyers', 'Mijozlarga'),
    )
    
    title = models.CharField(max_length=255)
    message = models.TextField()
    target = models.CharField(max_length=10, choices=TARGET_CHOICES, default='all')
    created_at = models.DateTimeField(auto_now_add=True)
    is_sent = models.BooleanField(default=False)  # Yuborilganligini belgilash uchun

    def __str__(self):
        return self.title

class UserNotification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    notification = models.ForeignKey(Notification, on_delete=models.CASCADE)
    is_read = models.BooleanField(default=False)
    received_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'notification')  # Har bir foydalanuvchi bir bildirishnomani faqat bir marta oladi

    def __str__(self):
        return f"{self.user.email} - {self.notification.title}"