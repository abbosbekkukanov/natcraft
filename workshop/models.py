from django.db import models
from django.conf import settings

class Workshop(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='workshop', unique=True)
    name = models.CharField(max_length=100)
    description = models.TextField()
    img = models.ImageField(upload_to='workshop_images/', null=True, blank=True)
    address = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class WorkshopImage360(models.Model):
    workshop = models.ForeignKey(Workshop, on_delete=models.CASCADE, related_name='images_360')
    image_360 = models.ImageField(upload_to='360_images/')

    def __str__(self):
        return f"360 image for {self.workshop.name}"

class WorkshopRating(models.Model):
    workshop = models.ForeignKey(Workshop, on_delete=models.CASCADE, related_name='ratings')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])  # 1-5 gacha baho
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('workshop', 'user')  # Har bir foydalanuvchi faqat bir marta baho bera oladi

    def __str__(self):
        return f"{self.rating} stars for {self.workshop.name}"