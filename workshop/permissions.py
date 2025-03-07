from rest_framework import permissions

class IsOwnerOrReadOnly(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        # Agar so'rov "GET", "HEAD" yoki "OPTIONS" bo'lsa, barcha foydalanuvchilarga ruxsat beriladi
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Agar so'rovni yuborgan foydalanuvchi workshop obyekti egasi bo'lsa, ruxsat beriladi
        return obj.user == request.user
