# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2017-02-23 11:08
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('leagues', '0014_auto_20170223_0505'),
    ]

    operations = [
        migrations.RenameField(
            model_name='league',
            old_name='league_abbrev',
            new_name='abbrev',
        ),
        migrations.RenameField(
            model_name='league',
            old_name='league_name',
            new_name='name',
        ),
        migrations.AlterUniqueTogether(
            name='league',
            unique_together=set([('abbrev', 'status'), ('name', 'status')]),
        ),
    ]