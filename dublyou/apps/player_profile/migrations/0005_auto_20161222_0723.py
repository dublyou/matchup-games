# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2016-12-22 13:23
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('player_profile', '0004_auto_20161221_0813'),
    ]

    operations = [
        migrations.RenameField(
            model_name='profile',
            old_name='birthdate',
            new_name='birth_date',
        ),
        migrations.RenameField(
            model_name='profile',
            old_name='sex',
            new_name='gender',
        ),
    ]
