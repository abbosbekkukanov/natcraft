from django.db import models
from django.conf import settings

class Workshop(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='workshops')
    name = models.CharField(max_length=100)
    description = models.TextField()
    image_360 = models.ImageField(upload_to='360_images/', null=True, blank=True)
    address = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
