from rest_framework import viewsets, generics, views, response, status
from .models import Banner, Craftsmanship, Craftsmanshiplist, SocialMediaLink, OurTeam, AboutUs
from accounts.models import UserProfile, Profession
from products.models import Product
from products.models import Category
from products.serializers import CategorySerializer
from workshop.models import Workshop
from .serializers import (
    BannerSerializer, 
    CraftsmanshipSerializer, 
    CraftsmanshipListSerializer, 
    SocialMediaLinkSerializer, 
    OurTeamSerializer, 
    AboutUsSerializer, 
    CraftsmenStatsSerializer, 
    CraftmanDetailSerializer
)
from .permissions import IsReadOnly 
from django.db.models import Count
# Create your views here.

class BannerViewSet(viewsets.ModelViewSet):
    permission_classes = [IsReadOnly]
    queryset = Banner.objects.all()
    serializer_class = BannerSerializer

class CraftsmanshipViewSet(viewsets.ModelViewSet):
    permission_classes = [IsReadOnly]
    queryset = Craftsmanship.objects.all()
    serializer_class = CraftsmanshipSerializer

class CraftsmanshipListViewSet(viewsets.ModelViewSet):
    permission_classes = [IsReadOnly]
    queryset = Craftsmanshiplist.objects.all()
    serializer_class = CraftsmanshipListSerializer

class AboutUsViewSet(viewsets.ModelViewSet):
    permission_classes = [IsReadOnly]
    queryset = AboutUs.objects.all()
    serializer_class = AboutUsSerializer

class OurteamViewSet(viewsets.ModelViewSet):
    permission_classes = [IsReadOnly]
    queryset = OurTeam.objects.all()
    serializer_class = OurTeamSerializer

class SocialMediaLinkViewSet(viewsets.ModelViewSet):
    permission_classes = [IsReadOnly]
    queryset = SocialMediaLink.objects.all()
    serializer_class = SocialMediaLinkSerializer


class CraftsmenStatsView(views.APIView):
    permission_classes = [IsReadOnly]

    def get(self, request):
        address = request.query_params.get('address', None)
        profession = request.query_params.get('profession', None)

        craftsmen = UserProfile.objects.filter(user__is_verified=True).select_related('user', 'profession')

        if address:
            craftsmen = craftsmen.filter(address__icontains=address)

        if profession:
            craftsmen = craftsmen.filter(profession__name__iexact=profession)

        total_craftsmen = craftsmen.count()

        craftsmen_by_profession = (
            Profession.objects.filter(profession__user__is_verified=True)
            .annotate(count=Count('profession'))
        )
        if address:
            craftsmen_by_profession = craftsmen_by_profession.filter(profession__address__icontains=address)
        if profession:
            craftsmen_by_profession = craftsmen_by_profession.filter(name__iexact=profession)
        craftsmen_by_profession_dict = {item['name']: item['count'] for item in craftsmen_by_profession.values('name', 'count')}

        workshops = Workshop.objects.filter(user__is_verified=True)
        if address:
            workshops = workshops.filter(user__profile__address__icontains=address)
        if profession:
            workshops = workshops.filter(user__profile__profession__name__iexact=profession)
        total_workshops = workshops.count()

        professions = Profession.objects.filter(profession__user__is_verified=True).distinct()
        if address:
            professions = professions.filter(profession__address__icontains=address)
        if profession:
            professions = professions.filter(name__iexact=profession)
        total_professions = professions.count()

        data = {
            'total_craftsmen': total_craftsmen,
            'craftsmen_by_profession': craftsmen_by_profession_dict,
            'total_workshops': total_workshops,
            'total_professions': total_professions, 
            'craftsmen': craftsmen,
        }
        serializer = CraftsmenStatsSerializer(data)
        return response.Response(serializer.data)
    
class CraftmanDetailView(views.APIView):
    permission_classes = [IsReadOnly]

    def get(self, request, id):
        try:
            craftsman = UserProfile.objects.get(id=id, user__is_verified=True)
            serializer = CraftmanDetailSerializer(craftsman, context={'request': request})
            return response.Response(serializer.data)
        except UserProfile.DoesNotExist:
            return response.Response({"detail": "Hunarmand topilmadi yoki tasdiqlanmagan."}, status=status.HTTP_404_NOT_FOUND)


class CategoryStatsView(views.APIView):
    permission_classes = [IsReadOnly]

    def get(self, request):
        categories = Category.objects.all()
        serializer = CategorySerializer(categories, many=True)
        return response.Response(serializer.data)