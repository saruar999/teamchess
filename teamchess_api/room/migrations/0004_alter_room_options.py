# Generated by Django 4.2 on 2024-05-22 13:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('room', '0003_room_password'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='room',
            options={'ordering': ['-created_at']},
        ),
    ]
