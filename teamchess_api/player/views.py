from rest_framework.response import Response
from rest_framework.generics import CreateAPIView, ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .models import Player
from .auth import TokenAuthentication
from .permissions import CanManipulatePlayer
from . import serializers


class BaseManipulatePlayerView(CreateAPIView):
    queryset = Player.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, CanManipulatePlayer]

    def create(self, request, *args, **kwargs):
        player = self.get_object()
        serializer = self.get_serializer(player, data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(status=status.HTTP_200_OK)


class KickPlayerView(BaseManipulatePlayerView):
    serializer_class = serializers.KickPlayerSerializer


class ChangePlayerSymbolView(BaseManipulatePlayerView):
    serializer_class = serializers.ChangePlayerSymbolSerializer


class PlayerInfoView(ListAPIView):
    serializer_class = serializers.PlayerSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)