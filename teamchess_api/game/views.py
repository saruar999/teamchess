from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
from player.permissions import IsRoomManager
from player.auth import TokenAuthentication
from . import serializers


class StartGameView(CreateAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsRoomManager]
    serializer_class = serializers.StartGameSerializer

