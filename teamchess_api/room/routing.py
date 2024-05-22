from channels.routing import URLRouter
from django.urls import path
from .consumers import RoomConsumer
from .auth import RoomWebSocketAuthentication


websocket_urlpatterns = RoomWebSocketAuthentication(URLRouter([
    path('room/<uuid:pk>/', RoomConsumer.as_asgi())
]))

