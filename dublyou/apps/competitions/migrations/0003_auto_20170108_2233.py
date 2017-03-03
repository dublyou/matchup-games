# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2017-01-09 04:33
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('competitions', '0002_auto_20161221_0813'),
    ]

    operations = [
        migrations.AlterField(
            model_name='competitorinfo',
            name='signup_method',
            field=models.IntegerField(choices=[(1, 'invite'), (2, 'league'), (3, 'individual signup'), (4, 'team signup')]),
        ),
    ]