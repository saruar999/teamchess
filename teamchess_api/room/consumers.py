from channels.generic.websocket import JsonWebsocketConsumer
from django.contrib.auth.models import AnonymousUser
from asgiref.sync import async_to_sync


class RoomConsumer(JsonWebsocketConsumer):
    
    @async_to_sync
    async def add_client_to_room(self):
        await self.channel_layer.group_add(str(self.room_id), self.channel_name)
        
    @async_to_sync
    async def remove_client_from_room(self):
        await self.channel_layer.group_discard(str(self.room_id), self.channel_name)
        
    @async_to_sync
    async def emit_to_group(self, content):
        await self.channel_layer.group_send(str(self.room_id), {**content, 'type': 'emit.message'})
        
    def set_player_channel_name(self):
        user = self.scope['user']
        user.channel_name = self.channel_name
        user.save()
    
    @staticmethod
    def serialize_user(user):
        return {'id': user.id, 'name': user.name, 'team': user.team, 'is_game_manager': user.is_game_manager}

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
                'message': 'player_joined_room', 
                'data': {'user': self.serialize_user(user)}
            }
        )

    def emit_message(self, event):
        self.send_json({
            'message': event['message'],
            'data': event['data']
        })
    
    def disconnect(self, code):
        self.emit_to_group(
            {
                'message': 'player_left_room',
                'data': {'user': self.serialize_user(self.scope['user'])}
            }
        )
        user = self.scope['user']
        user.delete()
    
    def kick_client(self, event):
        self.remove_client_from_room()
        self.emit_to_group(
            {
                'message': 'player_kicked',
                'data': {'user': self.serialize_user(self.scope['user'])}
            }
        )
        self.close()

    def player_symbol_changed(self, event):
        self.send_json({'message': 'player_symbol_changed'})
