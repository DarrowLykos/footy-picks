# Generated by Django 3.0.3 on 2020-04-14 15:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gameweek', '0002_auto_20200414_1543'),
    ]

    operations = [
        migrations.AlterField(
            model_name='team',
            name='thumbnail',
            field=models.ImageField(blank=True, upload_to='Team logos/'),
        ),
    ]
