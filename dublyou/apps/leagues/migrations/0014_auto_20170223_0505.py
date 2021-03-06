# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2017-02-23 11:05
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('leagues', '0013_auto_20170212_2327'),
    ]

    operations = [
        migrations.RenameField(
            model_name='team',
            old_name='team_abbrev',
            new_name='abbrev',
        ),
        migrations.RenameField(
            model_name='team',
            old_name='team_name',
            new_name='name',
        ),
        migrations.AlterField(
            model_name='team',
            name='captain',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='team_captain', to='profile.PlayerProfile'),
        ),
        migrations.AlterUniqueTogether(
            name='league',
            unique_together=set([]),
        ),
        migrations.AlterUniqueTogether(
            name='team',
            unique_together=set([('league', 'abbrev'), ('league', 'name')]),
        ),
    ]
