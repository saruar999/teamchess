# Generated by Django 4.2 on 2024-08-03 22:56

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='game',
            old_name='custom_board_fen',
            new_name='custom_fen',
        ),
        migrations.RenameField(
            model_name='game',
            old_name='board_fen',
            new_name='fen',
        ),
    ]
