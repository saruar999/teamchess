from rest_framework.serializers import ModelSerializer, Serializer, IntegerField
from rest_framework.exceptions import ValidationError
from .models import Player
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


class PlayerSerializer(ModelSerializer):

    class Meta:
        model = Player
        fields = ['id', 'name', 'team', 'player_symbol', 'is_game_manager']


class KickPlayerSerializer(Serializer):
    
    class Meta:
        fields = []
        
    @async_to_sync
    async def disconnect_client_from_websocket(self, channel_name):
        channel_layer = get_channel_layer()
        await channel_layer.send(channel_name, {'type': 'player.kicked'})
    
    def update(self, instance, validated_data):
        if instance.channel_name:
            self.disconnect_client_from_websocket(instance.channel_name)
        instance.delete()
        return {}


class ChangePlayerSymbolSerializer(ModelSerializer):
    
    class Meta:
        fields = ['player_symbol']
        model = Player
        extra_kwargs = {'player_symbol': {'write_only': True}}
    
    @async_to_sync    
    async def player_team_change_websocket(self, instance):
        channel_layer = get_channel_layer()
        await channel_layer.group_send(str(instance.room_id), {'type': 'player.symbol.changed'})
        
    def update(self, instance, validated_data):
        player_symbol = validated_data.get('player_symbol')
        room_id = instance.room_id

        if instance.player_symbol == player_symbol:
            raise ValidationError({'player_symbol': [f'Player is already assigned to this symbol.']})

        try:
            symbol_current_player = Player.objects.get(room_id=room_id, player_symbol=player_symbol)
        except Player.DoesNotExist:
            symbol_current_player = None

        if symbol_current_player is not None:
            symbol_current_player.player_symbol = instance.player_symbol
            symbol_current_player.save()

        instance.player_symbol = player_symbol
        instance.save()

        self.player_team_change_websocket(instance)
        return {}
