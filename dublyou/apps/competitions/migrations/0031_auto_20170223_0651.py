# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2017-02-23 12:51
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('competitions', '0030_auto_20170222_1251'),
    ]

    operations = [
        migrations.RenameField(
            model_name='competitioninvite',
            old_name='team',
            new_name='competitor',
        ),
    ]