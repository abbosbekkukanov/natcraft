from rest_framework import viewsets
from .models import Workshop
from .serializers import WorkshopSerializer
from .permissions import IsOwnerOrReadOnly

class WorkshopViewSet(viewsets.ModelViewSet):
    queryset = Workshop.objects.all()
    serializer_class = WorkshopSerializer
    permission_classes = [IsOwnerOrReadOnly]
