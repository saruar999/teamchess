from django.db import models


class Game(models.Model):
    fen = models.CharField(max_length=100)
    custom_fen = models.CharField(max_length=200)
    is_finished = models.BooleanField(default=False)
    room = models.OneToOneField(to='room.Room', on_delete=models.CASCADE, related_name='game')
