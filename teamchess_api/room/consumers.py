from channels.generic.websocket import WebsocketConsumer
from django.contrib.auth.models import AnonymousUser


class RoomConsumer(WebsocketConsumer):

    def connect(self):
        user = self.scope['user']
        if isinstance(user, AnonymousUser):
            self.close()

        room_id = self.scope['url_route']['kwargs']['pk']
        if user.room.id != room_id:
            self.close()

        self.accept()
