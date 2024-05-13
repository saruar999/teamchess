from rest_framework.generics import ListCreateAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from core.authentication import TokenAuthentication
from core.permission import CanAccessRoom
from .serializers import CreateRoomSerializer, ListRoomSerializer, RetrieveRoomSerializer
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