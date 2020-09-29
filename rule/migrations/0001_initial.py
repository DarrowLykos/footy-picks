# Generated by Django 3.0.3 on 2020-04-28 13:55

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Payout',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('position', models.IntegerField(default=1)),
                ('percentage', models.DecimalField(decimal_places=4, default=1, max_digits=10)),
                ('split_if_tied', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Rule',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('correct_score', models.IntegerField(default=0)),
                ('correct_result', models.IntegerField(default=0)),
                ('correct_home_score', models.IntegerField(default=0)),
                ('correct_away_score', models.IntegerField(default=0)),
                ('joker_count', models.IntegerField(default=0)),
                ('joker_multiplier', models.IntegerField(default=0)),
                ('payouts', models.ManyToManyField(related_name='rules', related_query_name='rule', to='rule.Payout')),
            ],
        ),
        migrations.CreateModel(
            name='RulePayout',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('payout', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='rule.Payout')),
                ('rule', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='rule.Rule')),
            ],
        ),
    ]