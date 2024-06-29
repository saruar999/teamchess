from rest_framework.serializers import ModelSerializer, CharField, ChoiceField, Serializer, IntegerField
from rest_framework.exceptions import ValidationError
from .auth import TokenAuthentication
from .models import Room, Player
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .consumers import RoomConsumer


class CreateRoomSerializer(ModelSerializer):

    player_name = CharField(max_length=50, write_only=True)
    player_team = ChoiceField(choices=Player.TeamChoices.choices, write_only=True)

    token = CharField(read_only=True)
    room_id = CharField(read_only=True)

    class Meta:
        model = Room
        fields = ['name', 'type', 'player_name', 'player_team', 'token', 'room_id', 'password']
        extra_kwargs = {
            'name': dict(write_only=True),
            'type': dict(write_only=True),
            'password': dict(write_only=True, required=False)
        }

    def validate(self, attrs):
        attrs = super(CreateRoomSerializer, self).validate(attrs)
        if attrs.get('type') == Room.RoomTypeChoices.PRIVATE and not attrs.get('password'):
            raise ValidationError({'password': ['Password is required for private rooms.']})
        return attrs

    def create(self, validated_data):
        room = Room.objects.create(
            name=validated_data.get('name'), type=validated_data.get('type'), password=validated_data.get('password')
        )
        player = Player.objects.create(
            name=validated_data.get('player_name'), team=validated_data.get('player_team'), is_game_manager=True,
            room=room
        )
        token = TokenAuthentication().generate_token(player)
        return {'token': token.key, 'room_id': room.id}


class ListRoomSerializer(ModelSerializer):

    class Meta:
        model = Room
        fields = ['id', 'name', 'type', 'status', 'created_at']


class PlayerSerializer(ModelSerializer):

    class Meta:
        model = Player
        fields = ['id', 'name', 'team', 'is_game_manager']


class RetrieveRoomSerializer(ListRoomSerializer):

    game = None
    players = PlayerSerializer(many=True)

    class Meta(ListRoomSerializer.Meta):
        fields = ListRoomSerializer.Meta.fields + ['players']


class JoinRoomSerializer(ModelSerializer):

    player_name = CharField(max_length=50, write_only=True)
    token = CharField(read_only=True)

    class Meta:
        model = Room
        fields = ['player_name', 'token', 'password']
        extra_kwargs = {
            'password': dict(write_only=True, required=False)
        }

    def validate(self, attrs):
        attrs = super(JoinRoomSerializer, self).validate(attrs)

        current_players = self.instance.players.all()
        if current_players.count() == 4:
            raise ValidationError({'non_field_errors': ['Room is full.']})

        if self.instance.type == Room.RoomTypeChoices.PRIVATE:
            if not attrs.get('password'):
                raise ValidationError({'password': ['Password is required for private room.']})
            if attrs.get('password') != self.instance.password:
                raise ValidationError({'password': ['Password is incorrect.']})

        white_count = current_players.filter(team=Player.TeamChoices.WHITE).count()
        if white_count < 2:
            team = Player.TeamChoices.WHITE
        else:
            team = Player.TeamChoices.BLACK

        attrs.update(team=team)
        return attrs

    def update(self, instance, validated_data):
        player = Player.objects.create(
            name=validated_data.get('player_name'), team=validated_data.get('team'), room=instance
        )
        token = TokenAuthentication().generate_token(player)
        return {'token': token}


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