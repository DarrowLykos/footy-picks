# Generated by Django 3.0.7 on 2020-09-01 15:12

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('gameweek', '0013_auto_20200701_1620'),
    ]

    operations = [
        migrations.AddField(
            model_name='game',
            name='last_update',
            field=models.DateTimeField(auto_now=True),
        ),
    ]