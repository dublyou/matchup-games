# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2017-01-29 05:49
from __future__ import unicode_literals

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('games', '0002_auto_20161214_1042'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('profile', '0010_auto_20170125_0125'),
    ]

    operations = [
        migrations.CreateModel(
            name='PlayerProfile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('privacy_type', models.IntegerField(choices=[(1, 'private'), (2, 'public')], default=1)),
                ('bio', models.CharField(max_length=200, null=True)),
                ('birth_date', models.DateField(null=True)),
                ('height', models.IntegerField(null=True)),
                ('weight', models.IntegerField(null=True)),
                ('gender', models.IntegerField(choices=[(0, 'male'), (1, 'female')], null=True)),
                ('abbrev', models.CharField(max_length=6, null=True, unique=True)),
                ('mobile_number', models.CharField(max_length=10, null=True, unique=True, validators=[django.core.validators.RegexValidator(message="Phone number must be entered in the format: '999999999'. Up to 10 digits allowed.", regex='^\\d{10}$')])),
                ('current_zip', models.CharField(max_length=5, null=True)),
                ('current_city', models.CharField(max_length=30, null=True)),
                ('current_state', models.CharField(max_length=3, null=True)),
                ('hometown_zip', models.CharField(max_length=5, null=True)),
                ('hometown_city', models.CharField(max_length=30, null=True)),
                ('hometown_state', models.CharField(max_length=3, null=True)),
                ('user_image', models.ImageField(null=True, upload_to='media/img/profile/user')),
                ('bg_image', models.FileField(null=True, upload_to='dublyou/static/img/profile/bg')),
                ('rating', models.DecimalField(decimal_places=4, default=0, max_digits=5)),
                ('creation_datetime', models.DateTimeField(auto_now_add=True)),
                ('favorite_game', models.ManyToManyField(to='games.GameType')),
                ('friends', models.ManyToManyField(related_name='_playerprofile_friends_+', to='profile.PlayerProfile')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='profile', to=settings.AUTH_USER_MODEL, verbose_name='user')),
            ],
            options={
                'verbose_name_plural': 'Profiles',
                'ordering': ('user',),
                'verbose_name': 'Profile',
            },
        ),
        migrations.RemoveField(
            model_name='profile',
            name='favorite_game',
        ),
        migrations.RemoveField(
            model_name='profile',
            name='friends',
        ),
        migrations.RemoveField(
            model_name='profile',
            name='user',
        ),
        migrations.DeleteModel(
            name='Profile',
        ),
    ]
