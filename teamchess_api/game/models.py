from django.db import models


class Game(models.Model):

    board_fen = models.CharField(max_length=100)
    is_finished = models.BooleanField(default=False)
