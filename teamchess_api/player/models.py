from django.db import models
from django.dispatch import receiver
from engine.constants import SYMBOL_COLOR_MAPPING


class Player(models.Model):
    REQUIRED_FIELDS = []
    USERNAME_FIELD = 'id'
    is_anonymous = False

    class TeamChoices(models.TextChoices):
        WHITE = 'white',
        BLACK = 'black'

    name = models.CharField(max_length=50)
    team = models.CharField(choices=TeamChoices.choices, max_length=5)
    is_game_manager = models.BooleanField(default=False)
    room = models.ForeignKey(to='room.Room', on_delete=models.CASCADE, related_name='players')
    channel_name = models.CharField(max_length=200, default=None, null=True)
    player_symbol = models.CharField(max_length=1)

    @property
    def is_authenticated(self):
        return True

    @staticmethod
    @receiver(models.signals.pre_save, sender='player.Player')
    def player_pre_save(sender, instance, **kwargs):
        instance.team = SYMBOL_COLOR_MAPPING[instance.player_symbol]
