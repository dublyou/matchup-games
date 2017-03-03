# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2017-01-12 09:05
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('competitions', '0007_auto_20170111_1308'),
    ]

    operations = [
        migrations.AlterField(
            model_name='competitorinfo',
            name='players_per_team',
            field=models.IntegerField(blank=True, choices=[(2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7), (8, 8), (9, 9), (10, 10), (11, 11), (12, 12), (13, 13), (14, 14), (15, 15), (16, 16), (17, 17), (18, 18), (19, 19), (20, 20), (21, 21), (22, 22), (23, 23), (24, 24), (25, 25), (26, 26), (27, 27), (28, 28), (29, 29), (30, 30), (31, 31), (32, 32)], null=True),
        ),
        migrations.AlterField(
            model_name='competitorinfo',
            name='split_teams',
            field=models.IntegerField(choices=[(1, 'random'), (2, 'manual')], default=1, null=True),
        ),
        migrations.AlterField(
            model_name='season',
            name='playoff_bids',
            field=models.IntegerField(choices=[(2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7), (8, 8), (9, 9), (10, 10), (11, 11), (12, 12), (13, 13), (14, 14), (15, 15), (16, 16), (17, 17), (18, 18), (19, 19), (20, 20), (21, 21), (22, 22), (23, 23), (24, 24), (25, 25), (26, 26), (27, 27), (28, 28), (29, 29), (30, 30), (31, 31), (32, 32)], null=True),
        ),
        migrations.AlterField(
            model_name='season',
            name='season_games',
            field=models.IntegerField(choices=[(2, 2), (4, 4), (6, 6), (8, 8), (10, 10), (12, 12), (14, 14), (16, 16), (18, 18), (20, 20), (22, 22), (24, 24), (26, 26), (28, 28), (30, 30), (32, 32), (34, 34), (36, 36), (38, 38), (40, 40), (42, 42), (44, 44), (46, 46), (48, 48), (50, 50), (52, 52), (54, 54), (56, 56), (58, 58), (60, 60), (62, 62), (64, 64), (66, 66), (68, 68), (70, 70), (72, 72), (74, 74), (76, 76), (78, 78), (80, 80), (82, 82), (84, 84), (86, 86), (88, 88), (90, 90), (92, 92), (94, 94), (96, 96), (98, 98), (100, 100), (102, 102), (104, 104), (106, 106), (108, 108), (110, 110), (112, 112), (114, 114), (116, 116), (118, 118), (120, 120), (122, 122), (124, 124), (126, 126), (128, 128), (130, 130), (132, 132), (134, 134), (136, 136), (138, 138), (140, 140), (142, 142), (144, 144), (146, 146), (148, 148), (150, 150), (152, 152), (154, 154), (156, 156), (158, 158), (160, 160), (162, 162)]),
        ),
        migrations.AlterField(
            model_name='series',
            name='series_games',
            field=models.IntegerField(choices=[(3, 3), (5, 5), (7, 7), (9, 9), (11, 11), (13, 13), (15, 15)]),
        ),
    ]