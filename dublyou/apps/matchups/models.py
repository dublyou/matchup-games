from django.db import models
from django.contrib.auth.models import User
from ...constants import COMP_TYPES, EVENT_TYPES, SERIES_TYPES, TOURNEY_TYPES, TOURNEY_SEEDS, SEASON_TYPES
from ..games.models import GameType, GameVenue
from ..leagues.models import League, Team, LeagueMember
# from django.core.validators import RegexValidator, EmailValidator
# from django.utils.translation import ugettext_lazy as _


class GameEvent(models.Model):
    event_name = models.CharField(max_length=30, null=True, blank=True)
    event_type = models.IntegerField(choices=EVENT_TYPES)
    game_type = models.ForeignKey(GameType, null=True)
    comp_type = models.IntegerField(choices=COMP_TYPES)
    num_children = models.IntegerField(default=1)
    parent_event = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)
    child_num = models.IntegerField(null=True)
    league = models.ForeignKey(League, null=True)
    final = models.BooleanField(default=False)
    creation_datetime = models.DateTimeField(auto_now_add=True)


class Season(models.Model):
    event = models.OneToOneField(GameEvent)
    season_type = models.IntegerField(choices=SEASON_TYPES)
    season_games = models.IntegerField()
    season_playoffs = models.BooleanField(default=False)


class Tournament(models.Model):
    event = models.OneToOneField(GameEvent)
    tourney_type = models.IntegerField(choices=TOURNEY_TYPES)
    tourney_seeds = models.IntegerField(choices=TOURNEY_SEEDS)


class TourneyRound(models.Model):
    tournament = models.ForeignKey(Tournament)
    round_type = models.IntegerField(choices=((1, "winner"), (2, "loser")))
    round_num = models.IntegerField()

    class Meta:
        unique_together = ("tournament", "round_type", "round_num")


class Series(models.Model):
    event = models.OneToOneField(GameEvent)
    series_type = models.IntegerField(choices=SERIES_TYPES)
    series_games = models.IntegerField()
    tourney_round = models.ForeignKey(TourneyRound, null=True)


class Game(models.Model):
    game_date = models.DateTimeField(null=True, blank=True)
    game_venue = models.ForeignKey(GameVenue, null=True)
    parent_event = models.ForeignKey(GameEvent)
    child_num = models.IntegerField(default=1)
    competitors = models.ManyToManyField(User, through='Matchup', null=True)
    teams = models.ManyToManyField(Team, through='TeamMatchup', null=True)
    tourney_round = models.ForeignKey(TourneyRound, null=True)
    final = models.BooleanField(default=False)
    witness_id = models.CharField(max_length=50, null=True)
    creation_datetime = models.DateTimeField(auto_now_add=True)


class Matchup(models.Model):
    game = models.ForeignKey(Game)
    competitor = models.ForeignKey(User, null=True)
    dependent_type = models.IntegerField(null=True, choices=((1, "winner"), (2, "loser"), (3, "series")))
    dependent_game = models.ForeignKey(Game)
    dependent_series = models.ForeignKey(Series)
    game_on = models.BooleanField(default=False)
    place = models.IntegerField(null=True, blank=True)
    score = models.IntegerField(null=True, blank=True)
    seed = models.IntegerField(null=True)

    class Meta:
        unique_together = ("game", "competitor", "dependent_game", "dependent_series")


class TeamMatchup(models.Model):
    game = models.ForeignKey(Game)
    competitor = models.ForeignKey(Team)
    dependent_type = models.IntegerField(choices=((1, "winner"), (2, "loser"), (3, "series")))
    dependent_game = models.ForeignKey(Game)
    dependent_series = models.ForeignKey(Series)
    game_on = models.BooleanField(default=False)
    place = models.IntegerField(null=True, blank=True)
    score = models.IntegerField(null=True, blank=True)
    seed = models.IntegerField()

    class Meta:
        unique_together = ("game", "competitor", "dependent_game", "dependent_series")


class SubTeam(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    member = models.ForeignKey(LeagueMember, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("game", "member")
