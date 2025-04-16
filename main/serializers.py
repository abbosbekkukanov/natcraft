from rest_framework import serializers
from accounts.models import UserProfile, Profession
from accounts.serializers import ProfessionSerializer
from products.models import Product
from products.serializers import ProductSerializer
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


class CraftsmanSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(source='user.first_name')
    experience = serializers.IntegerField()  # Tajriba yillari
    mentees = serializers.IntegerField()  # Shogirdlar soni
    award = serializers.CharField(allow_null=True)  # Sovrinlar
    profession = ProfessionSerializer()  # Hunarmandning kasbi

    class Meta:
        model = UserProfile
        fields = ['id', 'first_name', 'experience', 'mentees', 'award', 'profession']

class CraftsmenStatsSerializer(serializers.Serializer):
    total_craftsmen = serializers.IntegerField()
    craftsmen_by_profession = serializers.DictField(child=serializers.IntegerField())
    total_workshops = serializers.IntegerField()
    total_professions = serializers.IntegerField()
    craftsmen = CraftsmanSerializer(many=True) 

class CraftmanDetailSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(source='user.first_name')
    email = serializers.CharField(source='user.email')
    profession = ProfessionSerializer()
    products = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = ['id', 'first_name', 'email', 'bio', 'profile_image', 'address', 'latitude', 'longitude',
                  'phone_number', 'experience', 'mentees', 'award', 'profession', 'products']

    def get_products(self, obj):
        products = Product.objects.filter(user=obj.user)
        return ProductSerializer(products, many=True, context=self.context).data