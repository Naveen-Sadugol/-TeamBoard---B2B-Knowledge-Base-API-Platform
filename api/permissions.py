from rest_framework.permissions import BasePermission

from .models import Company


class IsAdminUser(BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return getattr(request.user.company, "role", None) == Company.Role.ADMIN
