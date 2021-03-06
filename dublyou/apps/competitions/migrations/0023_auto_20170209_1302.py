# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2017-02-09 19:02
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('profile', '0013_auto_20170209_1302'),
        ('games', '0002_auto_20161214_1042'),
        ('competitions', '0022_auto_20170208_1333'),
    ]

    operations = [
        migrations.CreateModel(
            name='Player',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rating', models.DecimalField(decimal_places=4, default=0, max_digits=5)),
                ('favorite_game', models.ManyToManyField(blank=True, to='games.GameType')),
                ('profile', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='player', to='profile.PlayerProfile')),
            ],
        ),
        migrations.AddField(
            model_name='matchupcompetitor',
            name='left',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='competition',
            name='status',
            field=models.IntegerField(choices=[(0, 'incomplete'), (1, 'upcoming'), (2, 'dependency'), (3, 'pending'), (4, 'finished'), (5, 'if necessary'), (6, 'overdue')], default=1),
        ),
        migrations.AlterField(
            model_name='matchup',
            name='status',
            field=models.IntegerField(choices=[(0, 'incomplete'), (1, 'upcoming'), (2, 'dependency'), (3, 'pending'), (4, 'finished'), (5, 'if necessary'), (6, 'overdue')], default=0),
        ),
        migrations.AlterField(
            model_name='season',
            name='status',
            field=models.IntegerField(choices=[(0, 'incomplete'), (1, 'upcoming'), (2, 'dependency'), (3, 'pending'), (4, 'finished'), (5, 'if necessary'), (6, 'overdue')], default=0),
        ),
        migrations.AlterField(
            model_name='series',
            name='status',
            field=models.IntegerField(choices=[(0, 'incomplete'), (1, 'upcoming'), (2, 'dependency'), (3, 'pending'), (4, 'finished'), (5, 'if necessary'), (6, 'overdue')], default=0),
        ),
        migrations.AlterField(
            model_name='tournament',
            name='status',
            field=models.IntegerField(choices=[(0, 'incomplete'), (1, 'upcoming'), (2, 'dependency'), (3, 'pending'), (4, 'finished'), (5, 'if necessary'), (6, 'overdue')], default=0),
        ),
        migrations.AlterUniqueTogether(
            name='matchupcompetitor',
            unique_together=set([('matchup', 'competitor'), ('dependent_outcome', 'dependent_type', 'dependent_id', 'seed')]),
        ),
    ]
