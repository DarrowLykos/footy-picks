# Generated by Django 3.0.7 on 2020-07-01 11:37

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('gameweek', '0011_league_rules'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='game',
            name='rules',
        ),
    ]
