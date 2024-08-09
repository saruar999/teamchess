from channels.generic.websocket import JsonWebsocketConsumer
from django.contrib.auth.models import AnonymousUser
from asgiref.sync import async_to_sync
from game.active_boards import ACTIVE_BOARDS
from .models import Room
from .serializers import RetrieveRoomSerializer


class RoomConsumer(JsonWebsocketConsumer):
    PLAYER_JOINED_ROOM = 'player_joined_room'
    PLAYER_LEFT_ROOM = 'player_left_room'
    PLAYER_KICKED = 'player_kicked'
    PLAYER_SYMBOL_CHANGED = 'player_symbol_changed'
    GAME_STARTED = 'game_started'

    # TODO: Update player model to track online/offline status.
    
    @async_to_sync
    async def add_client_to_room(self):
        await self.channel_layer.group_add(str(self.room_id), self.channel_name)
        
    @async_to_sync
    async def remove_client_from_room(self):
        await self.channel_layer.group_discard(str(self.room_id), self.channel_name)
        
    @async_to_sync
    async def emit_to_group(self, content):
        await self.channel_layer.group_send(str(self.room_id), {**content, 'type': 'emit.message'})

    def emit_message(self, event):
        self.send_json({'message': event['message'], 'data': event['data']})
        
    def set_player_channel_name(self):
        user = self.scope['user']
        user.channel_name = self.channel_name
        user.save()

    def delete_player(self):
        user = self.scope['user']
        user.delete()

    def serialize_room(self):
        room = Room.objects.prefetch_related('players').get(id=self.room_id)
        return RetrieveRoomSerializer(room).data

    def get_pieces(self):
        board = ACTIVE_BOARDS[self.room_id]
        return board.get_pieces()

    def connect(self):
        user = self.scope['user']
        if isinstance(user, AnonymousUser):
            self.close()

        self.room_id = self.scope['url_route']['kwargs']['pk']
        if user.room.id != self.room_id:
            self.close()

        self.accept()
        self.add_client_to_room()
        self.set_player_channel_name()
        self.emit_to_group(
            {
                'message': self.PLAYER_JOINED_ROOM,
                'data': {'room': self.serialize_room()}
            }
        )
    
    def disconnect(self, code):
        self.emit_to_group(
            {
                'message': self.PLAYER_LEFT_ROOM,
                'data': {'room': self.serialize_room()}
            }
        )
        self.remove_client_from_room()
        self.close(code=code)

    def player_kicked(self, event):
        self.emit_to_group(
            {
                'message': self.PLAYER_KICKED,
                'data': {'room': self.serialize_room()}
            }
        )
        self.remove_client_from_room()
        self.close(code=0, reason=self.PLAYER_KICKED)
        self.delete_player()

    def player_symbol_changed(self, event):
        self.send_json(
            {
                'message': self.PLAYER_SYMBOL_CHANGED,
                'data': {'room': self.serialize_room()}
            }
        )

    def game_started(self, event):
        self.send_json(
            {
                'message': self.GAME_STARTED,
                'data': {
                    'room': self.serialize_room(),
                    'pieces': self.get_pieces()
                }
            }
        )
