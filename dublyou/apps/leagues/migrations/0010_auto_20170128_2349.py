# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2017-01-29 05:49
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import smart_selects.db_fields


class Migration(migrations.Migration):

    dependencies = [
        ('leagues', '0009_auto_20170128_2349'),
        ('profile', '0011_auto_20170128_2349'),
    ]

    operations = [
        migrations.AddField(
            model_name='pendingplayer',
            name='player',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='league_invites', to='profile.PlayerProfile'),
        ),
        migrations.AddField(
            model_name='pendingplayer',
            name='team',
            field=smart_selects.db_fields.ChainedForeignKey(auto_choose=True, blank=True, chained_field='league', chained_model_field='league', null=True, on_delete=django.db.models.deletion.CASCADE, to='leagues.Team'),
        ),
        migrations.AddField(
            model_name='leagueplayer',
            name='division',
            field=smart_selects.db_fields.ChainedForeignKey(auto_choose=True, blank=True, chained_field='league', chained_model_field='league', null=True, on_delete=django.db.models.deletion.CASCADE, to='leagues.LeagueDivision'),
        ),
        migrations.AddField(
            model_name='leagueplayer',
            name='league',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='league_players', to='leagues.League'),
        ),
        migrations.AddField(
            model_name='leagueplayer',
            name='player',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='profile.PlayerProfile'),
        ),
        migrations.AddField(
            model_name='leagueplayer',
            name='team',
            field=smart_selects.db_fields.ChainedForeignKey(auto_choose=True, blank=True, chained_field='league', chained_model_field='league', null=True, on_delete=django.db.models.deletion.CASCADE, to='leagues.Team'),
        ),
        migrations.AddField(
            model_name='league',
            name='pending_players',
            field=models.ManyToManyField(related_name='pending_invites', through='leagues.PendingPlayer', to='profile.PlayerProfile'),
        ),
        migrations.AddField(
            model_name='league',
            name='players',
            field=models.ManyToManyField(related_name='leagues', through='leagues.LeaguePlayer', to='profile.PlayerProfile'),
        ),
        migrations.AddField(
            model_name='team',
            name='players',
            field=models.ManyToManyField(related_name='teams', through='leagues.LeaguePlayer', to='profile.PlayerProfile'),
        ),
        migrations.AlterUniqueTogether(
            name='pendingplayer',
            unique_together=set([('league', 'player', 'team')]),
        ),
        migrations.AlterUniqueTogether(
            name='leagueplayer',
            unique_together=set([('league', 'player')]),
        ),
    ]