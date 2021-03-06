# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2017-02-23 11:05
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('games', '0006_auto_20170221_0559'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='game',
            options={'ordering': ('name',)},
        ),
        migrations.AlterModelOptions(
            name='gamestat',
            options={'ordering': ('name',)},
        ),
        migrations.AddField(
            model_name='game',
            name='default_game',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='gamestat',
            name='abbrev',
            field=models.CharField(blank=True, max_length=4, null=True),
        ),
        migrations.AddField(
            model_name='gamestat',
            name='decimal_places',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='gamestat',
            name='formula',
            field=models.CharField(blank=True, max_length=30, null=True),
        ),
        migrations.AddField(
            model_name='gamestat',
            name='max_value',
            field=models.DecimalField(blank=True, decimal_places=4, max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name='gamestat',
            name='min_value',
            field=models.DecimalField(blank=True, decimal_places=4, max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name='gamestat',
            name='value_type',
            field=models.IntegerField(choices=[(1, 'number'), (2, 'percentage')], default=1),
        ),
        migrations.AlterUniqueTogether(
            name='gamestat',
            unique_together=set([('game', 'abbrev'), ('game', 'name')]),
        ),
    ]
