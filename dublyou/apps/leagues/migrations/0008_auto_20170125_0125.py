# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2017-01-25 07:25
from __future__ import unicode_literals

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('invitations', '0003_auto_20151126_1523'),
        ('leagues', '0007_auto_20170111_1230'),
    ]

    operations = [
        migrations.CreateModel(
            name='LeagueSignUpPage',
            fields=[
                ('verification_key', models.CharField(max_length=40, primary_key=True, serialize=False)),
                ('expiration', models.DateTimeField(blank=True, null=True)),
                ('msg_image', models.ImageField(blank=True, null=True, upload_to='media/img/leagues/signup')),
            ],
        ),
        migrations.CreateModel(
            name='PendingMember',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('expiration', models.DateTimeField(blank=True, null=True)),
                ('invite_type', models.IntegerField(choices=[(1, 'league'), (2, 'team'), (3, 'open')], default=1)),
                ('approved', models.BooleanField(default=False)),
                ('accepted', models.BooleanField(default=False)),
                ('division', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='leagues.LeagueDivision')),
                ('invite', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='pending_members', to='invitations.Invitation')),
            ],
        ),
        migrations.RemoveField(
            model_name='leaguerequest',
            name='league',
        ),
        migrations.RemoveField(
            model_name='leaguemember',
            name='pending',
        ),
        migrations.AddField(
            model_name='league',
            name='parent',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='sub_leagues', to='leagues.League'),
        ),
        migrations.AddField(
            model_name='league',
            name='status',
            field=models.IntegerField(choices=[(1, 'active'), (2, 'inactive')], default=1),
        ),
        migrations.AddField(
            model_name='leaguemember',
            name='seed',
            field=models.IntegerField(blank=True, default=1, null=True),
        ),
        migrations.AddField(
            model_name='team',
            name='status',
            field=models.IntegerField(choices=[(1, 'pending'), (2, 'active'), (3, 'inactive')], default=1),
        ),
        migrations.AlterField(
            model_name='league',
            name='base_city',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='league',
            name='game_type',
            field=models.ManyToManyField(blank=True, to='games.GameType'),
        ),
        migrations.AlterField(
            model_name='league',
            name='league_abbrev',
            field=models.CharField(blank=True, max_length=4, null=True),
        ),
        migrations.AlterField(
            model_name='league',
            name='league_bg',
            field=models.FileField(blank=True, null=True, upload_to='dublyou/static/img/league/bg'),
        ),
        migrations.AlterField(
            model_name='league',
            name='league_emblem',
            field=models.FileField(blank=True, null=True, upload_to='dublyou/static/img/league/emblem'),
        ),
        migrations.AlterField(
            model_name='league',
            name='league_name',
            field=models.CharField(max_length=30, validators=[django.core.validators.RegexValidator('^[-\\s\\.\\w\\d]{1,30}$')]),
        ),
        migrations.AlterField(
            model_name='leaguemember',
            name='division',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='leagues.LeagueDivision'),
        ),
        migrations.AlterField(
            model_name='leaguemember',
            name='member',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='leaguemember',
            name='status',
            field=models.IntegerField(choices=[(1, 'active'), (2, 'inactive')], default=1),
        ),
        migrations.AlterField(
            model_name='leaguemember',
            name='team',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='leagues.Team'),
        ),
        migrations.AlterField(
            model_name='team',
            name='captain',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='team_captain', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='team',
            name='division',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='leagues.LeagueDivision'),
        ),
        migrations.AlterField(
            model_name='team',
            name='max_members',
            field=models.IntegerField(default=10),
        ),
        migrations.AlterField(
            model_name='team',
            name='team_abbrev',
            field=models.CharField(blank=True, max_length=4, null=True),
        ),
        migrations.AlterField(
            model_name='team',
            name='team_name',
            field=models.CharField(max_length=30, validators=[django.core.validators.RegexValidator('^[-\\s\\.\\w\\d]{1,30}$')]),
        ),
        migrations.RemoveField(
            model_name='league',
            name='dummy_league',
        ),
        migrations.AlterUniqueTogether(
            name='league',
            unique_together=set([('league_name', 'status')]),
        ),
        migrations.DeleteModel(
            name='LeagueRequest',
        ),
        migrations.AddField(
            model_name='pendingmember',
            name='league',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='leagues.League'),
        ),
        migrations.AddField(
            model_name='pendingmember',
            name='team',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='leagues.Team'),
        ),
        migrations.AddField(
            model_name='pendingmember',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='leaguesignuppage',
            name='league',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='signup_page', to='leagues.League'),
        ),
        migrations.AlterUniqueTogether(
            name='pendingmember',
            unique_together=set([('league', 'user', 'team')]),
        ),
    ]