# Generated by Django 5.0.6 on 2024-05-12 23:54

import django.db.models.deletion
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Room',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid5, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=50)),
                ('type', models.CharField(choices=[('public', 'Public'), ('private', 'Private')], max_length=10)),
                ('status', models.CharField(choices=[('waiting', 'Waiting'), ('in_game', 'In Game'), ('cancelled', 'Cancelled'), ('closed', 'Closed')], default='waiting', max_length=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Player',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('team', models.CharField(choices=[('white', 'White'), ('black', 'Black')], max_length=5)),
                ('is_game_manager', models.BooleanField(default=False)),
                ('room', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='players', to='room.room')),
            ],
        ),
    ]
