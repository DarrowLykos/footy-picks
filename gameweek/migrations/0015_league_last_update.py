# Generated by Django 3.0.7 on 2020-09-01 15:32

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('gameweek', '0014_game_last_update'),
    ]

    operations = [
        migrations.AddField(
            model_name='league',
            name='last_update',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
