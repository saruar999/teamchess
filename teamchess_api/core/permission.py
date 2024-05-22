from rest_framework.permissions import BasePermission


class CanAccessRoom(BasePermission):
    """
    A simple permission class that works on endpoints with room objects, it will check whether
    the authenticated user can access this room or not, to prevent user accessing any room with
    a system generated token.
    """
    def has_object_permission(self, request, view, obj):
        return obj == request.auth.user.room

class CanManipulatePlayer(BasePermission):
    """
    A simple permission class that checks whether the authenticated user is the room manager, 
    since only room managers can manipulate other players, it also checks whether the manipulated player
    is in the same room as the room manager.
    """
    
    def has_permission(self, request, view):
        print(request.user.is_game_manager)
        return request.user.is_game_manager
    
    def has_object_permission(self, request, view, obj):
        print(obj.room, request.user.room)
        return obj.room == request.user.room