from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Workshop, WorkshopImage360, WorkshopRating
from .serializers import WorkshopSerializer, WorkshopImage360Serializer, WorkshopRatingSerializer
from .permissions import IsOwnerOrReadOnly

class WorkshopViewSet(viewsets.ModelViewSet):
    serializer_class = WorkshopSerializer
    permission_classes = [IsOwnerOrReadOnly]

    def get_queryset(self):
        # Barcha ustaxonalarni qaytaradi, lekin faqat o‘z ustaxonasini tahrir qilish mumkin
        return Workshop.objects.all()

    def perform_create(self, serializer):
        # Workshop yaratishda faqat joriy foydalanuvchi bog‘lanadi
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def my_workshop(self, request):
        # Faqat foydalanuvchining o‘z ustaxonasini qaytaradi
        try:
            workshop = Workshop.objects.get(user=request.user)
            serializer = self.get_serializer(workshop)
            return Response(serializer.data)
        except Workshop.DoesNotExist:
            return Response({"detail": "Sizda hali ustaxona yo‘q"}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['post'], permission_classes=[IsOwnerOrReadOnly])
    def add_image_360(self, request, pk=None):
        workshop = self.get_object()
        serializer = WorkshopImage360Serializer(data=request.data)
        if serializer.is_valid():
            serializer.save(workshop=workshop)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class WorkshopRatingViewSet(viewsets.ModelViewSet):
    serializer_class = WorkshopRatingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return WorkshopRating.objects.filter(workshop__id=self.kwargs['workshop_pk'])

    def perform_create(self, serializer):
        workshop = Workshop.objects.get(id=self.kwargs['workshop_pk'])
        serializer.save(user=self.request.user, workshop=workshop)