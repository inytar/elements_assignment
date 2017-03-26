from rest_framework import permissions


class IsAdminUserOrReadOnly(permissions.BasePermission):
    """Allow acces to non-safe methods to admin users only.

    An admin user has the property `.is_staff`.
    """

    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS or
            request.user and request.user.is_staff
        )
