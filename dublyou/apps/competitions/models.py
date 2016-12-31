from django.db import models
from django.contrib.auth.models import User
from ... import constants
from ..games.models import GameType, GameVenue, GameRule
from ..leagues.models import League, Team, LeagueMember
from . import managers
from django.template.loader import render_to_string
from django.urls import reverse
# from django.core.validators import RegexValidator, EmailValidator
# from django.utils.translation import ugettext_lazy as _


class Competition(models.Model):
    competition_type = models.IntegerField(choices=constants.COMPETITION_TYPES)
    name = models.CharField(null=True, max_length=50)
    game_type = models.ForeignKey(GameType, null=True)
    creation_datetime = models.DateTimeField(auto_now_add=True)
    status = models.IntegerField(choices=constants.STATUS_TYPES, default=0)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True)

    @property
    def league(self):
        if self.parent:
            return self.parent.competitor_info.league
        else:
            return self.competitor_info.league

    @property
    def matchup_type(self):
        if self.parent:
            return self.parent.competitor_info.matchup_type
        else:
            return self.competitor_info.matchup_type

    @property
    def creator(self):
        return self.league.commissioner

    @property
    def competitors(self):
        if self.matchup_type == 1:
            return self.league.league_members.all()
        else:
            return self.league.team_set.all()

    # Methods
    def get_absolute_url(self):
        return reverse('competition:detail', args=[str(self.id)])

    def save(self, *args, **kwargs):
        super(Competition, self).save(*args, **kwargs)

        if not self.competition_name:
            self.competition_name = "Competition {}".format(self.id)
        self.save()

    def __str__(self):
        return "{} | {}".format(self.competition_name, self.get_competition_type_display())


class CompetitorInfo(models.Model):
    SIGNUP_METHOD = (
        (1, "assigned"),
        (2, "league"),
        (3, "individual signup"),
        (4, "team signup")
    )
    signup_method = models.IntegerField(choices=SIGNUP_METHOD)
    matchup_type = models.IntegerField(choices=constants.MATCHUP_TYPES)
    split_teams = models.IntegerField(choices=constants.SPLIT_TEAMS, null=True)
    players_per_team = models.IntegerField(null=True)

    league = models.ForeignKey(League, null=True, related_name="competition_set")
    competition = models.OneToOneField(Competition, on_delete=models.CASCADE, primary_key=True)


class Season(models.Model):
    competition = models.ForeignKey(Competition, on_delete=models.CASCADE)
    season_type = models.IntegerField(choices=constants.SEASON_TYPES)
    season_games = models.IntegerField()
    season_playoffs = models.BooleanField(default=False)
    playoff_bids = models.IntegerField(null=True)
    playoff_format = models.IntegerField(choices=constants.TOURNEY_TYPES, null=True)
    status = models.IntegerField(choices=constants.STATUS_TYPES, default=0)


class Tournament(models.Model):
    competition = models.ForeignKey(Competition, on_delete=models.CASCADE)
    tourney_type = models.IntegerField(choices=constants.TOURNEY_TYPES)
    tourney_seeds = models.IntegerField(choices=constants.TOURNEY_SEEDS)
    status = models.IntegerField(choices=constants.STATUS_TYPES, default=0)


class TourneyRound(models.Model):
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE)
    round_type = models.IntegerField(choices=((1, "winner"), (2, "loser")), null=True)
    round_num = models.IntegerField(null=True)


class Series(models.Model):
    competition = models.ForeignKey(Competition, on_delete=models.CASCADE)
    series_type = models.IntegerField(choices=constants.SERIES_TYPES)
    series_games = models.IntegerField()
    status = models.IntegerField(choices=constants.STATUS_TYPES, default=0)
    tourney_round = models.ForeignKey(TourneyRound, null=True)
    child_num = models.IntegerField()


class Matchup(models.Model):
    competition = models.ForeignKey(Competition, on_delete=models.CASCADE)
    parent_type = models.IntegerField(choices=constants.COMPETITION_TYPES)
    parent_id = models.IntegerField(null=True)
    date = models.DateField(null=True)
    time = models.TimeField(null=True)
    venue = models.ForeignKey(GameVenue, null=True)
    witness = models.ForeignKey(User, null=True, related_name="witness")
    rules = models.ManyToManyField(GameRule)
    notes = models.CharField(max_length=500)
    child_num = models.IntegerField()
    tourney_round = models.ForeignKey(TourneyRound, null=True)
    status = models.IntegerField(choices=constants.STATUS_TYPES, default=0)

    @property
    def parent(self):
        if self.parent_type == 2:
            return Series.objects.get(id=self.parent_id)
        elif self.parent_type == 3:
            return Tournament.objects.get(id=self.parent_id)
        elif self.parent_type == 4:
            return Season.objects.get(id=self.parent_id)

    objects = managers.MatchupManager()
    players = models.ManyToManyField(User, through='MatchupMember', through_fields=('matchup', 'player'),
                                     related_name="matchups")
    teams = models.ManyToManyField(Team, through='MatchupMember', through_fields=('matchup', 'team'),
                                   related_name="matchups")


class MatchupMember(models.Model):
    matchup = models.ForeignKey(Matchup, on_delete=models.CASCADE)
    player = models.ForeignKey(User, null=True)
    team = models.ForeignKey(Team, null=True)
    dependent_outcome = models.IntegerField(null=True, choices=((1, "winner"), (2, "loser")))
    dependent_type = models.IntegerField(null=True, choices=((1, "matchup"), (2, "series"), (4, "season")))
    dependent_id = models.IntegerField(null=True)
    accepted = models.BooleanField(default=False)
    place = models.IntegerField(null=True)
    score = models.IntegerField(null=True)
    seed = models.IntegerField(null=True)

    class Meta:
        unique_together = ("matchup", "player", "team", "dependent_outcome", "dependent_type", "dependent_id", "seed")

    @property
    def dependent_text(self):
        return "{} of {}".format(self.get_dependent_outcome_display(), self.get_dependent_type_display())

    @property
    def opponents(self):
        if self.player:
            return self.matchup.players.exclude(id=self.player.id)
        elif self.team:
            return self.matchup.teams.exclude(id=self.team.id)

    def dependent(self):
        if self.dependent_type == 1:
            return Matchup.objects.get(id=self.dependent_id)
        elif self.dependent_type == 2:
            return Series.objects.get(id=self.dependent_id)
        elif self.dependent_type == 4:
            return Season.objects.get(id=self.dependent_id)


class SubTeam(models.Model):
    matchup = models.ForeignKey(Matchup, on_delete=models.CASCADE)
    member = models.ForeignKey(LeagueMember, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("matchup", "member")
