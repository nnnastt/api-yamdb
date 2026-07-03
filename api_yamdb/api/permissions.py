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
            and (
                request.user.is_staff  #временное решение пока не будет пользователей(если забуду исправить напомните мне)
                or request.user.is_superuser
            )
        )
