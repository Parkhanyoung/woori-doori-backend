from rest_framework.permissions import BasePermission

from .models import Profile


class IsProfileOnly(BasePermission):

    def has_object_permission(self, request, view, obj):
        return bool(Profile.objects.filter(user=request.user))
