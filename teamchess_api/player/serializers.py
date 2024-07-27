from rest_framework.serializers import ModelSerializer, Serializer, IntegerField
from rest_framework.exceptions import ValidationError
from .models import Player
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


class PlayerSerializer(ModelSerializer):

    class Meta:
        model = Player
        fields = ['id', 'name', 'team', 'is_game_manager']


class KickPlayerSerializer(Serializer):
    
    class Meta:
        fields = []
        
    @async_to_sync
    async def disconnect_client_from_websocket(self, channel_name):
        channel_layer = get_channel_layer()
        await channel_layer.send(channel_name, {'type': 'kick.client', 'code': 0})
        
    
    def update(self, instance, validated_data):
        self.disconnect_client_from_websocket(instance.channel_name)
        instance.delete()
        return {}

class ChangePlayerColorSerializer(ModelSerializer):
    
    class Meta:
        fields = ['team']
        model = Player
        extra_kwargs = {'team': {'write_only': True}}
    
    @async_to_sync    
    async def player_team_change_websocket(self, instance):
        channel_layer = get_channel_layer()
        await channel_layer.group_send(str(instance.room_id), {'type': 'player.team.changed'})

        
    def update(self, instance, validated_data):
        team = validated_data.get('team')
        room_id = instance.room_id
        
        if Player.objects.filter(room_id=room_id, team=team).count() == 2:
            raise ValidationError({'team': [f'Team {team} already has 2 players.']})
        
        if instance.team == team:
            raise ValidationError({'team': [f'Player is already on team {team}.']})

        instance.team = team
        instance.save()

        self.player_team_change_websocket(instance)
        return {}

class SwapPlayerSerializer(Serializer):
    
    swap_with = IntegerField(write_only=True)
    
    class Meta:
        fields = ['swap_with']
        
    @async_to_sync    
    async def players_swapped_websocket(self, instance):
        channel_layer = get_channel_layer()
        await channel_layer.group_send(str(instance.room_id), {'type': 'players.swapped'})
    
    def update(self, instance, validated_data):
        try:
            swap_with_player = Player.objects.get(id=validated_data.get('swap_with'), room=instance.room)
        except Player.DoesNotExist:
            raise ValidationError({'swap_with': ['Player does not exist in room.']})
        
        from_team = instance.team
        to_team = swap_with_player.team
        
        if from_team == to_team:
            raise ValidationError({'non_field_errors': ['Can not swap players inside same team.']})
        
        instance.team = to_team
        swap_with_player.team = from_team
        instance.save()
        swap_with_player.save()
        self.players_swapped_websocket(instance)
        return {}