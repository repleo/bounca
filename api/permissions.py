"""Permission classes for retrieving certificates"""

from rest_framework import permissions


class BounCAUserPermissions(permissions.BasePermission):
    def has_permission(self, request, view):
        if view.action == "list":
            return request.user.is_admin
        elif view.action == "retrieve":
            return True
        else:
            return False

    def has_object_permission(self, request, view, obj):
        if view.action == "retrieve":
            return request.user.is_admin or obj == request.user
        else:
            return False
