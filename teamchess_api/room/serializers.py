from rest_framework.serializers import ModelSerializer, CharField, ChoiceField
from core.authentication import TokenAuthentication
from .models import Room, Player


class CreateRoomSerializer(ModelSerializer):

    player_name = CharField(max_length=50, write_only=True)
    player_team = ChoiceField(choices=Player.TeamChoices.choices, write_only=True)

    token = CharField(read_only=True)
    room_id = CharField(read_only=True)

    class Meta:
        model = Room
        fields = ['name', 'type', 'player_name', 'player_team', 'token', 'room_id']
        extra_kwargs = {
            'name': dict(write_only=True),
            'type': dict(write_only=True)
        }

    def create(self, validated_data):
        room = Room.objects.create(name=validated_data.get('name'), type=validated_data.get('type'))
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
