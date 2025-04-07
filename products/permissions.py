from rest_framework import permissions

class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # GET so‘rovlariga ruxsat berish (faqat o‘qish uchun)
        if request.method in permissions.SAFE_METHODS:
            return True
        # POST, PUT, DELETE uchun faqat egasi ruxsatli
        return obj.user == request.user