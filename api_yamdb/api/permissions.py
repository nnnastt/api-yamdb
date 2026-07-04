from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Разрешение:
    - GET — доступно всем (включая анонимов)
    - POST, PATCH, DELETE — только администратору
    """

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return (
            request.user.is_authenticated
            and request.user.is_admin
        )


class IsAuthorModeratorAdminOrReadOnly(permissions.BasePermission):
    """
    Разрешение:
    - GET — доступно всем (включая анонимов)
    - POST, PATCH, DELETE — только автору, модератору или администратору
    """

    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or obj.author == request.user
            or request.user.is_moderator
        )


class IsAdminUser(permissions.BasePermission):
    """
    Разрешение только для администраторов.
    """

    def has_permission(self, request, view):
        return (
                request.user.is_authenticated
                and request.user.is_admin
        )