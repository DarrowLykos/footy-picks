# Generated by Django 3.0.7 on 2020-09-10 12:25

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('rule', '0002_auto_20200701_1119'),
    ]

    operations = [
        migrations.AddField(
            model_name='rule',
            name='joker_correct_result',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='rule',
            name='joker_correct_score',
            field=models.IntegerField(default=0),
        ),
    ]