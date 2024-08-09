from rest_framework import serializers
from rest_framework.settings import api_settings
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from game.models import Game
from room.models import Room
from engine.board import TeamChessBoard
from .active_boards import ACTIVE_BOARDS


class StartGameSerializer(serializers.ModelSerializer):

    room = serializers.PrimaryKeyRelatedField(queryset=Room.objects.all(), write_only=True)

    class Meta:
        model = Game
        fields = ('id', 'room', 'fen', 'custom_fen', 'is_finished')
        read_only_fields = ('id', 'fen', 'custom_fen', 'is_finished')

    def validate(self, attrs):
        attrs = super().validate(attrs)
        room = attrs['room']
        if hasattr(room, 'game'):
            raise serializers.ValidationError({
                api_settings.NON_FIELD_ERRORS_KEY: ['Game has already started.']
            })
        if room.players.filter(is_online=True).count() != 4:
            raise serializers.ValidationError({
                api_settings.NON_FIELD_ERRORS_KEY: ['Cannot start game with less than 4 players.']
            })
        return attrs

    @async_to_sync
    async def send_game_started_event(self, channel_name):
        channel_layer = get_channel_layer()
        await channel_layer.group_send(channel_name, {'type': 'game.started'})

    def create(self, validated_data):
        chessboard = TeamChessBoard()
        custom_fen = chessboard.fen()
        fen = chessboard.get_original_fen()

        game = Game.objects.create(room=validated_data.pop('room'), fen=fen, custom_fen=custom_fen)
        room = game.room
        room.status = Room.RoomStatusChoices.IN_GAME
        room.save()

        ACTIVE_BOARDS[room.id] = chessboard

        self.send_game_started_event(str(room.id))

        return game


class RetrieveGameSerializer(serializers.ModelSerializer):

    class Meta:
        model = Game
        fields = ('id', 'fen', 'custom_fen', 'is_finished')
