# Generated by Django 3.0.7 on 2020-10-02 14:29

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('gameweek', '0018_prediction_final'),
    ]

    operations = [
        migrations.AlterField(
            model_name='prediction',
            name='submit_date_time',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]