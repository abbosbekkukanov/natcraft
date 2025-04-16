from rest_framework import permissions


class IsAuthorOrReadOnly(permissions.BasePermission):
    """
    Hamma ko‘rishi mumkin (GET), faqat ro‘yxatdan o‘tgan foydalanuvchi post, put, delete qila oladi.
    PUT va DELETE esa faqat o'z ma'lumotiga.
    """

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True

        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        return obj.user == request.user