from rest_framework import permissions


class CanManageRole(permissions.BasePermission):
    """
    Object-level permission to only allow owners of an object to edit it.
    Assumes the model instance has an `owner` attribute.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.has_permission(['list_role', 'create_role'])

    def has_object_permission(self, request, view, obj):
        return request.user.is_authenticated and request.user.has_permission(['list_role', 'delete_role', 'update_role'])
