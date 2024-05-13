from rest_framework.permissions import BasePermission


class CanAccessRoom(BasePermission):
    """
    A simple permission class that works on endpoints with room objects, it will check whether
    the authenticated user can access this room or not, to prevent user accessing any room with
    a system generated token.
    """
    def has_object_permission(self, request, view, obj):
        return obj == request.auth.user.room