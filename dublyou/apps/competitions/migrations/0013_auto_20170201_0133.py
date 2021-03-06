# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2017-02-01 07:33
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profile', '0012_auto_20170130_1013'),
        ('competitions', '0012_auto_20170130_1013'),
    ]

    operations = [
        migrations.AddField(
            model_name='competition',
            name='invitees',
            field=models.ManyToManyField(related_name='invited_competitions', through='competitions.CompetitionInvite', to='profile.PlayerProfile'),
        ),
        migrations.AddField(
            model_name='competitioninvite',
            name='creation_datetime',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
    ]
