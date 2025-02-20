from rest_framework import serializers
from .models import Banner, Craftsmanship, Craftsmanshiplist, OurTeam, SocialMediaLink, AboutUs, FeatureItem, CraftsmanshipFeature

class BannerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Banner
        fields = '__all__'


class CraftsmanshipSerializer(serializers.ModelSerializer):
    class Meta:
        model = Craftsmanship
        fields = '__all__'

class FeatureItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeatureItem
        fields = ['name', 'description']


class CraftsmanshipFeatureSerializer(serializers.ModelSerializer):
    items = FeatureItemSerializer(many=True, read_only=True)

    class Meta:
        model = CraftsmanshipFeature
        fields = ['key', 'items']

class CraftsmanshipListSerializer(serializers.ModelSerializer):
    features = CraftsmanshipFeatureSerializer(many=True, read_only=True)

    class Meta:
        model = Craftsmanshiplist
        fields = '__all__'


class AboutUsSerializer(serializers.ModelSerializer):
    class Meta:
        model = AboutUs
        fields = '__all__'


class OurTeamSerializer(serializers.ModelSerializer):
    about_us = AboutUsSerializer()

    class Meta: 
        model = OurTeam
        fields = '__all__'


class SocialMediaLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = SocialMediaLink
        fields = '__all__'