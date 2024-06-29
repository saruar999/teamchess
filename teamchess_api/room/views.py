from rest_framework.generics import ListCreateAPIView, RetrieveAPIView, CreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .auth import TokenAuthentication
from .permission import CanAccessRoom, CanManipulatePlayer
from . import serializers
from .models import Room, Player


class ListCreateRoomView(ListCreateAPIView):
    queryset = Room.objects.all()

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return serializers.ListRoomSerializer
        else:
            return serializers.CreateRoomSerializer


class RetrieveRoomView(RetrieveAPIView):
    serializer_class = serializers.RetrieveRoomSerializer
    queryset = Room.objects.prefetch_related('players')
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, CanAccessRoom]


class JoinRoomView(CreateAPIView):
    serializer_class = serializers.JoinRoomSerializer
    queryset = Room.objects.all()

    def create(self, request, *args, **kwargs):
        room = self.get_object()
        serializer = self.get_serializer(room, data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_200_OK)


class KickPlayerView(CreateAPIView):
    serializer_class = serializers.KickPlayerSerializer
    queryset = Player.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, CanManipulatePlayer]
    
    def create(self, request, *args, **kwargs):
        player = self.get_object()
        serializer = self.get_serializer(player, data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(status=status.HTTP_200_OK)

class ChangePlayerTeamView(CreateAPIView):
    serializer_class = serializers.ChangePlayerColorSerializer
    queryset = Player.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, CanManipulatePlayer]
    
    def create(self, request, *args, **kwargs):
        player = self.get_object()
        serializer = self.get_serializer(player, data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(status=status.HTTP_200_OK)
    

class SwapPlayerView(CreateAPIView):
    serializer_class = serializers.SwapPlayerSerializer
    queryset = Player.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, CanManipulatePlayer]
    
    def create(self, request, *args, **kwargs):
        player = self.get_object()
        serializer = self.get_serializer(player, data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(status=status.HTTP_200_OK)