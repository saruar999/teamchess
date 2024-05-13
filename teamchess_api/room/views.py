from rest_framework.generics import ListCreateAPIView, RetrieveAPIView, CreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from core.authentication import TokenAuthentication
from core.permission import CanAccessRoom
from .serializers import CreateRoomSerializer, ListRoomSerializer, RetrieveRoomSerializer, JoinRoomSerializer
from .models import Room


class ListCreateRoomView(ListCreateAPIView):
    queryset = Room.objects.all()

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return ListRoomSerializer
        else:
            return CreateRoomSerializer


class RetrieveRoomView(RetrieveAPIView):
    serializer_class = RetrieveRoomSerializer
    queryset = Room.objects.prefetch_related('players')
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, CanAccessRoom]


class JoinRoomView(CreateAPIView):
    serializer_class = JoinRoomSerializer
    queryset = Room.objects.all()

    def create(self, request, *args, **kwargs):
        room = self.get_object()
        serializer = self.get_serializer(room, data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_200_OK)
