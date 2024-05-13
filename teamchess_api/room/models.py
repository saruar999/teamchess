from django.db import models
from uuid import uuid4
from django_cryptography.fields import encrypt


class Room(models.Model):

    class RoomTypeChoices(models.TextChoices):
        PUBLIC = 'public',
        PRIVATE = 'private'

    class RoomStatusChoices(models.TextChoices):
        WAITING = 'waiting',
        IN_GAME = 'in_game',
        CANCELLED = 'cancelled',
        CLOSED = 'closed'

    id = models.UUIDField(primary_key=True, default=uuid4)
    name = models.CharField(max_length=50)
    type = models.CharField(choices=RoomTypeChoices.choices, max_length=10)
    status = models.CharField(choices=RoomStatusChoices.choices, max_length=10, default=RoomStatusChoices.WAITING)
    # game = models.OneToOneField(to='game.models.Game', on_delete=models.CASCADE, null=True, default=None)
    created_at = models.DateTimeField(auto_now_add=True)
    password = encrypt(models.CharField(max_length=100, null=True, default=None))

    class Meta:
        ordering = ['-created_at']


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
    room = models.ForeignKey(to=Room, on_delete=models.CASCADE, related_name='players')

    @property
    def is_authenticated(self):
        return True
