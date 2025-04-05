from rest_framework import permissions

class IsChatParticipant(permissions.BasePermission):
    """Faqat chatdagi sotuvchi yoki xaridor ruxsatga ega bo‘ladi"""
    
    def has_object_permission(self, request, view, obj):
        # Foydalanuvchi chatning sotuvchisi yoki xaridori ekanligini tekshirish
        return obj.seller == request.user or obj.buyer == request.user