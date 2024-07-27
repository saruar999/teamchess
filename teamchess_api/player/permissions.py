from rest_framework.permissions import BasePermission


class CanManipulatePlayer(BasePermission):
    """
    A simple permission class that checks whether the authenticated user is the room manager, 
    since only room managers can manipulate other players, it also checks whether the manipulated player
    is in the same room as the room manager.
    """
    
    def has_permission(self, request, view):
        return request.user.is_game_manager
    
    def has_object_permission(self, request, view, obj):
        return obj.room == request.user.room