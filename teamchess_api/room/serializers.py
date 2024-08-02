from rest_framework.serializers import ModelSerializer, CharField, ChoiceField
from rest_framework.exceptions import ValidationError
from player.auth import TokenAuthentication
from .models import Room
from player.models import Player
from player.serializers import PlayerSerializer
from engine.constants import *


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
            room=room, player_symbol=SPADE
        )
        token = TokenAuthentication().generate_token(player)
        return {'token': token.key, 'room_id': room.id}


class ListRoomSerializer(ModelSerializer):

    class Meta:
        model = Room
        fields = ['id', 'name', 'type', 'status', 'created_at']


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

        # Assigning player symbol to the player.
        player_symbol = None
        for symbol in PLAYER_SYMBOLS:
            if not current_players.filter(player_symbol=symbol).exists():
                player_symbol = symbol

        attrs.update(player_symbol=player_symbol)
        return attrs

    def update(self, instance, validated_data):
        player = Player.objects.create(
            name=validated_data.get('player_name'), room=instance,
            player_symbol=validated_data.get('player_symbol')
        )
        token = TokenAuthentication().generate_token(player)
        return {'token': token}
