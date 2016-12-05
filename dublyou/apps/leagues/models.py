from django.db import models
from django.contrib.auth.models import User
from ...constants import COMP_TYPES
from ..games.models import GameType
# from django.core.validators import RegexValidator, EmailValidator
# from django.utils.translation import ugettext_lazy as _


class League(models.Model):
    league_name = models.CharField(max_length=30)
    comp_type = models.IntegerField(choices=COMP_TYPES)
    league_members = models.ManyToManyField(User, through='LeagueMember', related_name="members")
    game_type = models.ManyToManyField(GameType)
    commissioner = models.ForeignKey(User, related_name="commissioner")
    base_city = models.CharField(max_length=20, null=True)
    max_members = models.IntegerField(null=True, blank=True)
    creation_datetime = models.DateTimeField(auto_now_add=True)


class LeagueDivision(models.Model):
    league = models.ForeignKey(League, on_delete=models.CASCADE)
    division_name = models.CharField(max_length=30)

    class Meta:
        unique_together = ("league", "division_name")


class Team(models.Model):
    league = models.ForeignKey(League, on_delete=models.CASCADE)
    team_name = models.CharField(max_length=30)
    team_abbrev = models.CharField(max_length=4, null=True)
    captain = models.ForeignKey(User, on_delete=models.CASCADE)
    max_members = models.IntegerField(null=True)
    division = models.ForeignKey(LeagueDivision, null=True)
    creation_datetime = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("league", "team_name")


class LeagueMember(models.Model):
    league = models.ForeignKey(League, on_delete=models.CASCADE)
    member = models.ForeignKey(User, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, null=True)
    division = models.ForeignKey(LeagueDivision, null=True)
    admin = models.BooleanField(default=False)
    creation_datetime = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("league", "member")

