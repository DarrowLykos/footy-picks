# Generated by Django 3.0.3 on 2020-05-01 13:24

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('team', '0001_initial'),
        ('gameweek', '0002_league_accepts_members'),
    ]

    operations = [
        migrations.AlterField(
            model_name='game',
            name='matches',
            field=models.ManyToManyField(blank=True, related_name='games', related_query_name='game', to='team.Match'),
        ),
    ]
