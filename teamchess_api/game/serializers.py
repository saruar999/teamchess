from rest_framework import serializers
from rest_framework.settings import api_settings
from rest_framework.validators import UniqueValidator

from engine.constants import PLAYER_SYMBOLS
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
        if room.players.count() != 4:
            raise serializers.ValidationError({
                api_settings.NON_FIELD_ERRORS_KEY: ['Cannot start game with less than 4 players.']
            })
        return attrs

    def create(self, validated_data):
        chessboard = TeamChessBoard()
        custom_fen = chessboard.fen()

        fen = custom_fen
        for player_symbol in PLAYER_SYMBOLS:
            fen = fen.replace(player_symbol, '')

        game = Game.objects.create(room=validated_data.pop('room'), fen=fen, custom_fen=custom_fen)
        ACTIVE_BOARDS[game.id] = chessboard
        return game
