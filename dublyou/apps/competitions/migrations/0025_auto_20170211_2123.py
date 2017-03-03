# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2017-02-12 03:23
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('leagues', '0012_auto_20170202_0320'),
        ('competitions', '0024_auto_20170210_1312'),
    ]

    operations = [
        migrations.AlterField(
            model_name='season',
            name='playoff_bids',
            field=models.IntegerField(blank=True, choices=[(2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7), (8, 8), (9, 9), (10, 10), (11, 11), (12, 12), (13, 13), (14, 14), (15, 15), (16, 16), (17, 17), (18, 18), (19, 19), (20, 20), (21, 21), (22, 22), (23, 23), (24, 24), (25, 25), (26, 26), (27, 27), (28, 28), (29, 29), (30, 30), (31, 31), (32, 32)], null=True),
        ),
        migrations.AlterField(
            model_name='season',
            name='playoff_format',
            field=models.IntegerField(blank=True, choices=[(1, 'single elimination'), (2, 'double elimination'), (3, 'series best of')], null=True),
        ),
        migrations.AlterUniqueTogether(
            name='competitor',
            unique_together=set([('competition', 'team'), ('competition', 'team_name')]),
        ),
    ]