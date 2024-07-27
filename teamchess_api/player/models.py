from django.db import models

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

    @property
    def is_authenticated(self):
        return True

