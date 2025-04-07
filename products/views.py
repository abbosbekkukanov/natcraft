from rest_framework import viewsets, permissions, generics
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.decorators import action
from rest_framework import status
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
from .models import Product, Category, Favorite, CartItem, Comment, ViewedProduct
from .serializers import ProductSerializer, CategorySerializer,  CommentSerializer, ViewedProductSerializer, FavoriteSerializer, CartItemSerializer
from .permissions import IsOwnerOrReadOnly

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


    # Kategoriya nomi bo'yicha barcha mahsulotlarni olish uchun yangi action
    @action(detail=False, methods=['get'], url_path='(?P<category_name>[^/]+)')
    def category_products(self, request, category_name=None):
        try:
            # Kategoriya nomiga ko'ra kategoriya olish
            category = Category.objects.get(name=category_name)
            # Ushbu kategoriya bo'yicha barcha mahsulotlarni olish
            products = Product.objects.filter(category=category)
            serializer = ProductSerializer(products, many=True)
            return Response(serializer.data)
        except Category.DoesNotExist:
            return Response({"detail": "Kategoriya topilmadi"}, status=404)
        

# class StandardPagination(PageNumberPagination):
#     page_size = 10  # Har bir sahifada 10 ta mahsulot
#     page_size_query_param = 'page_size'  # Foydalanuvchi sahifa hajmini o‘zgartirishi mumkin
#     max_page_size = 100  


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsOwnerOrReadOnly, permissions.IsAuthenticatedOrReadOnly]
    # pagination_class = StandardPagination
    # filter_backends = [DjangoFilterBackend, SearchFilter]
    # filterset_fields = ['price', 'category']
    # search_fields = ['name', 'description']

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    # Foydalanuvchining o‘z mahsulotlarini ko‘rish uchun yangi action
    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def my_products(self, request):
        """Foydalanuvchining o‘z mahsulotlarini qaytaradi"""
        products = Product.objects.filter(user=request.user)
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)

    # Maxsus action - kategoriya nomi va mahsulot ID'si bilan mahsulotni olish
    @action(detail=False, methods=['get'], url_path='categories/(?P<category_name>[^/]+)/(?P<product_id>\d+)')
    def retrieve_product_in_category(self, request, category_name=None, product_id=None):
        try:
            category = Category.objects.get(name=category_name)
            product = Product.objects.get(id=product_id, category=category)
            serializer = ProductSerializer(product)
            return Response(serializer.data)
        except Category.DoesNotExist:
            return Response({"detail": "Kategoriya topilmadi"}, status=status.HTTP_404_NOT_FOUND)
        except Product.DoesNotExist:
            return Response({"detail": "Bu kategoriyada mahsulot topilmadi"}, status=status.HTTP_404_NOT_FOUND)


    @action(detail=True, methods=['post'])
    def like(self, request, pk=None):
        product = self.get_object()
        favorite, created = Favorite.objects.get_or_create(user=request.user, product=product)
        if not created:
            favorite.delete()  # Agar allaqachon yoqdirilgan bo'lsa, yoqdirishni olib tashlash
            return Response({'status': 'unliked'})
        return Response({'status': 'liked'})

    @action(detail=True, methods=['post'])
    def add_to_cart(self, request, pk=None):
        product = self.get_object()
        cart_item, created = CartItem.objects.get_or_create(user=request.user, product=product)
        if not created:
            cart_item.quantity += 1  # Agar allaqachon savatchada bo'lsa, miqdorini oshirish
            cart_item.save()
        return Response({'status': 'added to cart', 'quantity': cart_item.quantity})
    
    # 19.11.2024
    
    @action(detail=True, methods=['get'], url_path='view')
    def record_view(self, request, pk=None):
        """Mahsulotni ko'rish va ko'rilganligini qayd etish"""
        product = self.get_object()
        # Ko'rishlar sonini oshirish
        product.view_count = models.F('view_count') + 1
        product.save()
        if request.user.is_authenticated:
            ViewedProduct.objects.create(user=request.user, product=product)

        product.refresh_from_db()  
        return Response({'status': 'view recorded', 'view_count': product.view_count})
    
class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsOwnerOrReadOnly, permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

# 19.19.2024

class LastViewedProductsView(generics.ListAPIView):
    serializer_class = ViewedProductSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Foydalanuvchining oxirgi ko‘rgan mahsulotlari"""
        return ViewedProduct.objects.filter(user=self.request.user).select_related('product')
