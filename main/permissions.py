from rest_framework import permissions

class IsReadOnly(permissions.BasePermission):
    """
    Foydalanuvchilar faqat ma'lumotni o'qish (GET) imkoniyatiga ega bo'ladi.
    """

    def has_permission(self, request, view):
        # Faqat GET so'rovlariga ruxsat beriladi
        if request.method in permissions.SAFE_METHODS:
            return True
        return False
