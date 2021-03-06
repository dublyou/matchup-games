# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2016-12-14 16:42
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('games', '0002_auto_20161214_1042'),
        ('leagues', '0002_auto_20161214_1042'),
    ]

    operations = [
        migrations.CreateModel(
            name='Competition',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('competition_type', models.IntegerField(choices=[(1, 'matchup'), (2, 'series'), (3, 'tournament'), (4, 'season'), (5, 'olympics')])),
                ('competition_name', models.CharField(max_length=50, null=True)),
                ('creation_datetime', models.DateTimeField(auto_now_add=True)),
                ('status', models.IntegerField(choices=[(0, 'incomplete'), (1, 'upcoming'), (2, 'dependency'), (3, 'in progress'), (4, 'finished'), (5, 'if necessary'), (6, 'overdue')], default=0)),
            ],
        ),
        migrations.CreateModel(
            name='Matchup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('parent_type', models.IntegerField(choices=[(1, 'matchup'), (2, 'series'), (3, 'tournament'), (4, 'season'), (5, 'olympics')])),
                ('parent_id', models.IntegerField(null=True)),
                ('date', models.DateTimeField(null=True)),
                ('notes', models.CharField(max_length=500)),
                ('child_num', models.IntegerField()),
                ('status', models.IntegerField(choices=[(0, 'incomplete'), (1, 'upcoming'), (2, 'dependency'), (3, 'in progress'), (4, 'finished'), (5, 'if necessary'), (6, 'overdue')], default=0)),
            ],
        ),
        migrations.CreateModel(
            name='MatchupCompetitor',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dependent_outcome', models.IntegerField(choices=[(1, 'winner'), (2, 'loser')], null=True)),
                ('dependent_type', models.IntegerField(choices=[(1, 'matchup'), (2, 'series'), (4, 'season')], null=True)),
                ('dependent_id', models.IntegerField(null=True)),
                ('accepted', models.BooleanField(default=False)),
                ('place', models.IntegerField(null=True)),
                ('score', models.IntegerField(null=True)),
                ('seed', models.IntegerField(null=True)),
                ('matchup', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='competitions.Matchup')),
                ('player', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('team', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='leagues.Team')),
            ],
        ),
        migrations.CreateModel(
            name='Season',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('season_type', models.IntegerField(choices=[(1, 'round robin'), (2, 'input')])),
                ('season_games', models.IntegerField()),
                ('season_playoffs', models.BooleanField(default=False)),
                ('playoff_bids', models.IntegerField(null=True)),
                ('playoff_format', models.IntegerField(choices=[(1, 'single elimination'), (2, 'double elimination'), (3, 'series best of')], null=True)),
                ('status', models.IntegerField(choices=[(0, 'incomplete'), (1, 'upcoming'), (2, 'dependency'), (3, 'in progress'), (4, 'finished'), (5, 'if necessary'), (6, 'overdue')], default=0)),
            ],
        ),
        migrations.CreateModel(
            name='Series',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('series_type', models.IntegerField(choices=[(1, 'best of'), (2, 'first to'), (3, 'play all')])),
                ('series_games', models.IntegerField()),
                ('status', models.IntegerField(choices=[(0, 'incomplete'), (1, 'upcoming'), (2, 'dependency'), (3, 'in progress'), (4, 'finished'), (5, 'if necessary'), (6, 'overdue')], default=0)),
                ('child_num', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='SubTeam',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('matchup', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='competitions.Matchup')),
                ('member', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='leagues.LeagueMember')),
                ('team', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='leagues.Team')),
            ],
        ),
        migrations.CreateModel(
            name='Tournament',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tourney_type', models.IntegerField(choices=[(1, 'single elimination'), (2, 'double elimination'), (3, 'series best of')])),
                ('tourney_seeds', models.IntegerField(choices=[(1, 'random'), (2, 'assigned')])),
                ('status', models.IntegerField(choices=[(0, 'incomplete'), (1, 'upcoming'), (2, 'dependency'), (3, 'in progress'), (4, 'finished'), (5, 'if necessary'), (6, 'overdue')], default=0)),
            ],
        ),
        migrations.CreateModel(
            name='TourneyRound',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('round_type', models.IntegerField(choices=[(1, 'winner'), (2, 'loser')], null=True)),
                ('round_num', models.IntegerField(null=True)),
                ('tournament', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='competitions.Tournament')),
            ],
        ),
        migrations.CreateModel(
            name='CompetitorInfo',
            fields=[
                ('signup_method', models.IntegerField(choices=[(1, 'assigned'), (2, 'league'), (3, 'individual signup'), (4, 'team signup')])),
                ('matchup_type', models.IntegerField(choices=[(1, 'individual'), (2, 'team')])),
                ('split_teams', models.IntegerField(choices=[(1, 'random'), (2, 'manual')], null=True)),
                ('players_per_team', models.IntegerField(null=True)),
                ('competition', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='competitions.Competition')),
                ('league', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='leagues.League')),
            ],
        ),
        migrations.AddField(
            model_name='tournament',
            name='competition',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='competitions.Competition'),
        ),
        migrations.AddField(
            model_name='series',
            name='competition',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='competitions.Competition'),
        ),
        migrations.AddField(
            model_name='series',
            name='tourney_round',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='competitions.TourneyRound'),
        ),
        migrations.AddField(
            model_name='season',
            name='competition',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='competitions.Competition'),
        ),
        migrations.AddField(
            model_name='matchup',
            name='competition',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='competitions.Competition'),
        ),
        migrations.AddField(
            model_name='matchup',
            name='players',
            field=models.ManyToManyField(related_name='matchups', through='competitions.MatchupCompetitor', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='matchup',
            name='rules',
            field=models.ManyToManyField(to='games.GameRule'),
        ),
        migrations.AddField(
            model_name='matchup',
            name='teams',
            field=models.ManyToManyField(related_name='matchups', through='competitions.MatchupCompetitor', to='leagues.Team'),
        ),
        migrations.AddField(
            model_name='matchup',
            name='tourney_round',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='competitions.TourneyRound'),
        ),
        migrations.AddField(
            model_name='matchup',
            name='venue',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='games.GameVenue'),
        ),
        migrations.AddField(
            model_name='matchup',
            name='witness',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='witness', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='competition',
            name='game_type',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='games.GameType'),
        ),
        migrations.AddField(
            model_name='competition',
            name='parent',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='competitions.Competition'),
        ),
        migrations.AlterUniqueTogether(
            name='subteam',
            unique_together=set([('matchup', 'member')]),
        ),
        migrations.AlterUniqueTogether(
            name='matchupcompetitor',
            unique_together=set([('matchup', 'player', 'team', 'dependent_outcome', 'dependent_type', 'dependent_id', 'seed')]),
        ),
    ]
