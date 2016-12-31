from django.db import models
from django.contrib.auth.models import User
from ...constants import MATCHUP_TYPES
from ..games.models import GameType
# from django.core.validators import RegexValidator, EmailValidator
# from django.utils.translation import ugettext_lazy as _


class League(models.Model):
    league_name = models.CharField(max_length=30)
    league_abbrev = models.CharField(max_length=4, null=True)
    matchup_type = models.IntegerField(choices=MATCHUP_TYPES)
    league_members = models.ManyToManyField(User, through='LeagueMember', related_name="leagues")
    game_type = models.ManyToManyField(GameType)
    commissioner = models.ForeignKey(User, related_name="commissioner")
    base_city = models.CharField(max_length=20, null=True)
    max_members = models.IntegerField(null=True, blank=True)
    league_emblem = models.FileField(upload_to="dublyou/static/img/league/emblem", null=True)
    league_bg = models.FileField(upload_to="dublyou/static/img/league/bg", null=True)
    dummy_league = models.BooleanField(default=False)
    privacy_type = models.IntegerField(choices=((1, "private"), (2, "public")), default=1)
    creation_datetime = models.DateTimeField(auto_now_add=True)

    @property
    def competitions(self):
        return self.competition_set.prefetch_related('competition').all()

    def __str__(self):
        return self.league_name + (" ({})".format(self.league_abbrev) if self.league_abbrev else "")


class LeagueDivision(models.Model):
    league = models.ForeignKey(League, on_delete=models.CASCADE)
    division_name = models.CharField(max_length=30)

    class Meta:
        unique_together = ("league", "division_name")


class Team(models.Model):
    league = models.ForeignKey(League, on_delete=models.CASCADE)
    team_name = models.CharField(max_length=30)
    team_abbrev = models.CharField(max_length=4, null=True)
    captain = models.ForeignKey(User, on_delete=models.CASCADE, related_name="team_captain")
    max_members = models.IntegerField(null=True)
    division = models.ForeignKey(LeagueDivision, null=True)
    team_logo = models.FileField(upload_to="dublyou/static/img/team/logo", null=True)
    team_bg = models.FileField(upload_to="dublyou/static/img/team/bg", null=True)
    creation_datetime = models.DateTimeField(auto_now_add=True)

    roster = models.ManyToManyField(User, through='LeagueMember', through_fields=('team', 'member'),
                                    related_name="team_set")

    class Meta:
        unique_together = ("league", "team_name")

    def __str__(self):
        return self.team_name + (" ({})".format(self.team_abbrev) if self.team_abbrev else "")


class LeagueMember(models.Model):
    league = models.ForeignKey(League, on_delete=models.CASCADE)
    member = models.ForeignKey(User, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, null=True)
    division = models.ForeignKey(LeagueDivision, null=True)
    admin = models.BooleanField(default=False)
    creation_datetime = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("league", "member")

