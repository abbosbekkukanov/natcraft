from rest_framework import permissions


class IsAuthorOrReadOnly(permissions.BasePermission):
    """
    Foydalanuvchi faqat o'zini yaratgan ma'lumotni o'zgartirishi mumkin.
    """

    def has_object_permission(self, request, view, obj):
        # Faqat o'qish ruxsati
        if request.method in permissions.SAFE_METHODS:
            return True

        # Yozish ruxsati faqat user uchun
        return obj.user == request.user
