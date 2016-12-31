# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2016-12-14 16:42
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('leagues', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='league',
            name='dummy_league',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='league',
            name='league_abbrev',
            field=models.CharField(max_length=4, null=True),
        ),
        migrations.AddField(
            model_name='league',
            name='league_bg',
            field=models.FileField(null=True, upload_to='dublyou/static/img/league/bg'),
        ),
        migrations.AddField(
            model_name='league',
            name='league_emblem',
            field=models.FileField(null=True, upload_to='dublyou/static/img/league/emblem'),
        ),
        migrations.AddField(
            model_name='team',
            name='team_bg',
            field=models.FileField(null=True, upload_to='dublyou/static/img/team/bg'),
        ),
        migrations.AddField(
            model_name='team',
            name='team_logo',
            field=models.FileField(null=True, upload_to='dublyou/static/img/team/logo'),
        ),
        migrations.AlterField(
            model_name='league',
            name='league_members',
            field=models.ManyToManyField(related_name='leagues', through='leagues.LeagueMember', to=settings.AUTH_USER_MODEL),
        ),
    ]