# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2016-12-04 17:50
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='GameRule',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rule', models.CharField(max_length=50)),
                ('rule_type', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='GameType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('game_name', models.CharField(max_length=30, unique=True)),
                ('game_class', models.IntegerField(choices=[(1, 'Sport'), (2, 'Race'), (3, 'Board Game'), (4, 'Card Game'), (5, 'Video Game'), (6, 'Bar Game'), (7, 'Other')])),
                ('game_subclass', models.CharField(max_length=25)),
                ('game_rules', models.TextField(max_length=500)),
                ('comp_type', models.IntegerField(choices=[(1, 'individual'), (2, 'team')])),
                ('comp_per_team', models.IntegerField(blank=True, null=True)),
                ('creation_datetime', models.DateTimeField(auto_now_add=True)),
                ('creator', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='GameVenue',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('venue_name', models.CharField(max_length=30, unique=True)),
                ('street_address', models.CharField(max_length=50)),
                ('city', models.CharField(max_length=20)),
                ('state', models.CharField(choices=[('AL', 'Alabama'), ('AK', 'Alaska'), ('AZ', 'Arizona'), ('AR', 'Arkansas'), ('CA', 'California'), ('CO', 'Colorado'), ('CT', 'Connecticut'), ('DE', 'Delaware'), ('DC', 'Dist of Columbia'), ('FL', 'Florida'), ('GA', 'Georgia'), ('HI', 'Hawaii'), ('ID', 'Idaho'), ('IL', 'Illinois'), ('IN', 'Indiana'), ('IA', 'Iowa'), ('KS', 'Kansas'), ('KY', 'Kentucky'), ('LA', 'Louisiana'), ('ME', 'Maine'), ('MD', 'Maryland'), ('MA', 'Massachusetts'), ('MI', 'Michigan'), ('MN', 'Minnesota'), ('MS', 'Mississippi'), ('MO', 'Missouri'), ('MT', 'Montana'), ('NE', 'Nebraska'), ('NV', 'Nevada'), ('NH', 'New Hampshire'), ('NJ', 'New Jersey'), ('NM', 'New Mexico'), ('NY', 'New York'), ('NC', 'North Carolina'), ('ND', 'North Dakota'), ('OH', 'Ohio'), ('OK', 'Oklahoma'), ('OR', 'Oregon'), ('PA', 'Pennsylvania'), ('RI', 'Rhode Island'), ('SC', 'South Carolina'), ('SD', 'South Dakota'), ('TN', 'Tennessee'), ('TX', 'Texas'), ('UT', 'Utah'), ('VT', 'Vermont'), ('VA', 'Virginia'), ('WA', 'Washington'), ('WV', 'West Virginia'), ('WI', 'Wisconsin'), ('WY', 'Wyoming')], max_length=2)),
                ('zip_code', models.CharField(max_length=5)),
                ('venue_type', models.IntegerField(choices=[(1, 'private'), (2, 'public')])),
                ('game_type', models.ManyToManyField(to='games.GameType')),
            ],
        ),
        migrations.AddField(
            model_name='gamerule',
            name='game_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='games.GameType'),
        ),
    ]