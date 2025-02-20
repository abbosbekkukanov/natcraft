from django.db import models
from django.utils import timezone  
from products.models import Category

# Create your models here.
class AbstractCard(models.Model):
    name = models.CharField(max_length=450)
    text = models.TextField()
    img = models.ImageField(upload_to='images/', null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True    


    def __str__(self):
        return self.name

class Banner(AbstractCard):
    img = models.ImageField(upload_to='banner/', null=True, blank=True)
    author = models.CharField(max_length=200, default='Unknown')
    video = models.FileField(upload_to='banner/', null=True, blank=True)

class AboutUs(models.Model):
    title = models.CharField(max_length=200, default='Mission and History')   
    mission = models.TextField()
    history = models.TextField()

    def __str__(self):
        return self.title

class OurTeam(AbstractCard):
    img = models.ImageField(upload_to='ourteam/', null=True, blank=True)
    profession = models.CharField(max_length=200)

    about_us = models.ForeignKey(AboutUs, on_delete=models.SET_NULL, related_name="about_us", null=True, blank=True)

class CommonCraftCard(models.Model):
    title = models.CharField(max_length=255)
    text = models.TextField()
    img = models.ImageField(upload_to='craftsmanship/', null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True    

    def __str__(self):
        return self.title
    

class Craftsmanship(CommonCraftCard):
    pass

class Craftsmanshiplist(CommonCraftCard):
    image = models.ImageField(upload_to='craftsmanship/', null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="craftsmanship_list", null=True, blank=True)

    def __str__(self):
        return self.category.name

class CraftsmanshipFeature(models.Model):
    craftsmanship = models.ForeignKey(
        Craftsmanshiplist, 
        on_delete=models.CASCADE, 
        related_name="features"
    )
    key = models.CharField(max_length=255)

    def __str__(self):
        return self.key

class FeatureItem(models.Model):
    feature = models.ForeignKey(
        CraftsmanshipFeature, 
        on_delete=models.CASCADE, 
        related_name="items"
    )
    name = models.CharField(max_length=255)
    description = models.TextField()

    def __str__(self):
        return self.name


class SocialMediaLink(models.Model):
    name = models.CharField(max_length=150)
    url = models.URLField()
    icon = models.ImageField(upload_to='social_media_icons/', null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name