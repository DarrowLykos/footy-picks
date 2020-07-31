# Generated by Django 3.0.3 on 2020-04-28 13:55

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Competition',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('country', models.CharField(
                    choices=[('ENG', 'England'), ('WOR', 'World'), ('EUR', 'Europe'), ('SCO', 'Scotland'),
                             ('ESP', 'Spain'), ('FRA', 'France'), ('GER', 'Germany')], default='ENG', max_length=100)),
                ('comp_type', models.CharField(
                    choices=[('DOL', 'Domestic League'), ('DOC', 'Domestic Cup'), ('INC', 'International Cup'),
                             ('DOF', 'Domestic Friendly'), ('INF', 'International Friendly'),
                             ('INQ', 'International Qualifiers')], default='DOL', max_length=3,
                    verbose_name='Competition Type')),
                ('thumbnail', models.ImageField(blank=True, upload_to='Media/Competition logos/', verbose_name='Logo')),
            ],
        ),
        migrations.CreateModel(
            name='Team',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('short_name', models.CharField(max_length=3)),
                ('thumbnail', models.ImageField(blank=True, upload_to='Media/Team logos/', verbose_name='Logo')),
                ('country', models.CharField(
                    choices=[('ENG', 'England'), ('WOR', 'World'), ('EUR', 'Europe'), ('SCO', 'Scotland'),
                             ('ESP', 'Spain'), ('FRA', 'France'), ('GER', 'Germany')], default='ENG', max_length=3)),
                ('competitions', models.ManyToManyField(to='team.Competition')),
            ],
        ),
        migrations.CreateModel(
            name='Match',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ko_date', models.DateTimeField(verbose_name='Kick Off')),
                ('home_score', models.IntegerField(blank=True, null=True)),
                ('away_score', models.IntegerField(blank=True, null=True)),
                ('penalties', models.BooleanField(default=False)),
                ('extra_time', models.BooleanField(default=False)),
                ('postponed', models.BooleanField(default=False)),
                ('result', models.CharField(
                    choices=[('Home90', 'Home win in 90 minutes'), ('Draw90', 'Draw in 90 minutes'),
                             ('Away90', 'Away win in 90 minutes'), ('Home120', 'Home win in Extra Time'),
                             ('Away120', 'Away win in Extra Time'), ('HomePens', 'Home win after Penalties'),
                             ('AwayPens', 'Away win after Penalties'), ('ToPlay', 'Still to be played')],
                    default='ToPlay', max_length=8)),
                ('away_team',
                 models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='away_matches',
                                   related_query_name='away_match', to='team.Team')),
                ('competition', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='team.Competition')),
                ('home_team',
                 models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='home_matches',
                                   related_query_name='home_match', to='team.Team')),
            ],
            options={
                'verbose_name': 'Match',
                'verbose_name_plural': 'Matches',
            },
        ),
    ]
