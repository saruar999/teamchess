from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from game.active_boards import ACTIVE_BOARDS
from .models import Room
from .serializers import RetrieveRoomSerializer


class RoomConsumer(AsyncJsonWebsocketConsumer):
    PLAYER_JOINED_ROOM = 'player_joined_room'
    PLAYER_DISCONNECTED = 'player_disconnected'
    PLAYER_KICKED = 'player_kicked'
    PLAYER_SYMBOL_CHANGED = 'player_symbol_changed'
    GAME_STARTED = 'game_started'

    async def add_client_to_room(self):
        await self.channel_layer.group_add(str(self.room_id), self.channel_name)
        
    async def remove_client_from_room(self):
        await self.channel_layer.group_discard(str(self.room_id), self.channel_name)
        
    async def emit_to_group(self, content):
        await self.channel_layer.group_send(str(self.room_id), {**content, 'type': 'emit.message'})

    async def emit_message(self, event):
        await self.send_json({'message': event['message'], 'data': event['data']})

    @database_sync_to_async
    def set_player_channel_name(self):
        user = self.scope['user']
        user.channel_name = self.channel_name
        user.is_online = True
        return user.save()

    @database_sync_to_async
    def delete_player(self):
        user = self.scope['user']
        return user.delete()

    @database_sync_to_async
    def serialize_room(self):
        room = Room.objects.prefetch_related('players').get(id=self.room_id)
        return RetrieveRoomSerializer(room).data

    @database_sync_to_async
    def set_user_offline(self):
        user = self.scope['user']
        user.is_online = False
        return user.save()

    @database_sync_to_async
    def get_user_room(self):
        return self.scope['user'].room

    def get_pieces(self):
        board = ACTIVE_BOARDS[self.room_id]
        return board.get_pieces()

    async def close(self, code=None, reason=None):
        await self.set_user_offline()
        await super().close(code=code, reason=reason)

    async def connect(self):
        user = self.scope['user']
        if isinstance(user, AnonymousUser):
            await self.close(code=3000, reason='Token invalid or session expired')

        self.room_id = self.scope['url_route']['kwargs']['pk']
        room = await self.get_user_room()
        if room.id != self.room_id:
            await self.close(code=3003, reason='Player room does not match this room')

        if user.is_online:
            await self.close(code=3003, reason='Player already online on different client')

        await self.accept()
        await self.add_client_to_room()
        await self.set_player_channel_name()
        await self.emit_to_group(
            {
                'message': self.PLAYER_JOINED_ROOM,
                'data': {'room': await self.serialize_room()}
            }
        )
    
    async def disconnect(self, code):
        await self.remove_client_from_room()
        await self.close(code=code)
        await self.emit_to_group(
            {
                'message': self.PLAYER_DISCONNECTED,
                'data': {'room': await self.serialize_room()}
            }
        )

    async def player_kicked(self, event):
        await self.emit_to_group(
            {
                'message': self.PLAYER_KICKED,
                'data': {'room': await self.serialize_room()}
            }
        )
        await self.remove_client_from_room()
        await self.close(code=1000, reason=self.PLAYER_KICKED)
        await self.delete_player()

    async def player_symbol_changed(self, event):
        await self.send_json(
            {
                'message': self.PLAYER_SYMBOL_CHANGED,
                'data': {'room': await self.serialize_room()}
            }
        )

    async def game_started(self, event):
        await self.send_json(
            {
                'message': self.GAME_STARTED,
                'data': {
                    'room': await self.serialize_room(),
                    'pieces': self.get_pieces()
                }
            }
        )
