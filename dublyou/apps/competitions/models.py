import math
import random
import sys
from itertools import combinations
from copy import deepcopy
from collections import OrderedDict

from django.db import models
from django.db.models import Model, Count, Case, When, Sum, Value, Max, F
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.core.validators import RegexValidator
from django.contrib.auth.models import User

from invitations.models import Invitation
from smart_selects.db_fields import ChainedForeignKey

from . import managers
from ..games.models import Game, GameVenue
from ..leagues.models import League, Team, LeagueInvite
from ..profile.models import Profile
from ... import constants
from ...abstract_models import BaseProfileModel, NAME_REGEX
from ...utils import upload_to_path, record_string, send_notification
# from django.core.validators import RegexValidator, EmailValidator


class Competition(Model):
    name = models.CharField(max_length=30, validators=[RegexValidator(NAME_REGEX)], null=True, blank=True)
    competition_type = models.IntegerField(choices=constants.COMPETITION_TYPES)
    league = models.ForeignKey(League, related_name="competitions", null=True, blank=True)
    game = models.ForeignKey(Game, null=True, blank=True)
    matchup_type = models.IntegerField(choices=constants.MATCHUP_TYPES, default=1)
    split_teams = models.IntegerField(choices=constants.SPLIT_TEAMS, default=1)
    players_per_team = models.IntegerField(choices=constants.PLAYERS_PER_TEAM, null=True, blank=True)
    date = models.DateField(null=True, blank=True)
    time = models.TimeField(null=True, blank=True)
    venue = models.ForeignKey(GameVenue, null=True, blank=True)
    notes = models.CharField(max_length=500, null=True, blank=True)
    creator = models.ForeignKey(Profile, related_name="created_competitions")
    creation_datetime = models.DateTimeField(auto_now_add=True, editable=False)
    status = models.IntegerField(choices=constants.STATUS_TYPES, default=0)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name="children")
    invitees = models.ManyToManyField(Profile, related_name="invited_competitions",
                                      through="CompetitionInvite")
    teams = models.ManyToManyField(Team, through='Competitor', related_name="team_competitions")

    @property
    def competitors(self):
        if self.seeds.exists():
            seeds = self.seeds.order_by("seed").values_list("competitor", flat=True)
            return Competitor.objects.filter(id__in=seeds)
        if self.parent:
            return self.parent.competitors
        return self.competitor_set.all()

    @property
    def players(self):
        competitors = self.parent.competitor_set if self.parent else self.competitor_set
        players = competitors.prefetch_related("players").values_list("players", flat=True).distinct("players").all()
        return [v for k, v in Profile.objects.in_bulk(players).items()]

    @property
    def matchup_competitors(self):
        return MatchupCompetitor.objects.filter(matchup__in=list(self.matchups.values_list("id"))).all()

    @property
    def competition_details(self):
        if self.competition_type in range(2, 5):
            attr = "{}_set".format(self.get_competition_type_display())
            queryset = getattr(self, attr, None)
            if queryset:
                return queryset.first()
        return False

    @property
    def upcoming_matchups(self):
        return self.matchups.filter(status__in=[1, 2]).order_by('date', 'child_num').all()

    @property
    def matchup_results(self):
        return self.matchups.filter(status__in=[3, 4]).order_by('-date', '-child_num').all()

    @property
    def events(self):
        if self.competition_type == 5:
            return self.children.all()
        return False

    @property
    def results(self):
        if self.competition_type != 5:
            finished, result = self.competition_details.results
            return result
        else:
            places = ["first", "second", "third"]
            standings = {}
            for c in self.competitors:
                line = OrderedDict()
                line.update({"competitor": c,
                             "avg_place": 0,
                             "events": 0})
                for place in places:
                    line[place] = 0
                standings[c.id] = deepcopy(line)
            for event in self.competition_set.all():
                finished, result = event.results
                if finished:
                    for c in result:
                        x = standings[c["competitor"].id]
                        place = c["place"]
                        events = x["events"]
                        x["avg_place"] = (x["avg_place"] * events + place)/(events + 1)
                        x["events"] += 1
                        if place in range(1, 4):
                            x[places[place - 1]] += 1
            return sorted(list(standings.values()), key=lambda k: (k['avg_place'], -k['first'], -k['second'], -k['third']))

    @property
    def profile_image(self):
        if self.parent:
            return self.parent.profile_image
        return "/static/svg/profile_competition.png"

    @property
    def description(self):
        if self.competition_type == 5:
            competition_details = "{} Event Olympics".format(self.children.count())
        else:
            competition_details = self.competition_details
        return "{} {}. {}".format(self.name, competition_details, self.notes)

    @property
    def date_formatted(self):
        if self.date:
            return self.date.strftime('%A %b %-d, %Y')
        return False

    @property
    def time_formatted(self):
        if self.time:
            return self.time.strftime('%-I:%M %p')
        return False

    # Methods
    def get_absolute_url(self):
        return reverse('competition', kwargs={"pk": self.pk})

    def save(self, *args, **kwargs):
        super(Competition, self).save(*args, **kwargs)
        if self.parent and self.status > 2 and self.parent.status == 1:
            self.parent.status = 3
            self.parent.save()
        if not self.name:
            self.name = "Competition {}".format(self.id)
            self.save()

    def add_competitor(self, player=None, team=None, invite=None):
        params = {"competitor_type": self.matchup_type}
        competitor = None
        if invite:
            player = invite.player
            competitor = invite.team
        elif team:
            competitor = team
        if player:
            self.invites.filter(player=player).delete()
            if player not in self.players:
                params["captain"] = player
                if self.matchup_type == 2 and not team:
                    params["status"] = 0
                    params["captain"] = None
                if competitor:
                    competitor.players.add(player)
                    competitor.status = 1
                    competitor.save()
                else:
                    competitor = self.competitor_set.create(**params)
                    competitor.players.add(player)
                    if self.competition_type == 3:
                        competitor.add_seed(self.seeds.count() + 1)
                return competitor

    def get_competitor(self, player):
        for competitor in self.competitors:
            if player in competitor.players.all():
                return competitor
        return False

    def update_status(self, matchup=None):
        status = self.status
        child_status = self.competition_details.status
        if child_status == 4:
            status = 4
        status = 1 if status == 2 else (3 if status != 4 else status)
        self.status = status
        self.save()
        if self.parent:
            self.parent.update_status()

    def invite_league(self):
        kwargs = {"competition": self, "approved": True}
        for player in self.league.league_players:
            kwargs["player"] = player.player
            kwargs["team"] = player.team
            CompetitionInvite.create(**kwargs)

    def create_matchups(self):
        def create_instance(comp_type, kwargs):
            instance_params = deepcopy(default_params)
            instance_params.update(kwargs)
            instance_params["competition"] = instance_params.get("competition") or self
            comp_models = [Matchup, Series, Tournament, Season]
            return comp_models[comp_type - 1].objects.create(**instance_params)

        def create_matchup(**kwargs):
            competitors = kwargs.pop("competitors", None) or self.competitors
            parent = kwargs.pop("parent", None)
            instance = create_instance(1, kwargs)
            instance.set_parent(parent)

            for c in competitors:
                params = {"matchup": instance}
                if isinstance(c, Competitor):
                    params["competitor"] = c
                elif isinstance(c, dict):
                    params.update(c)
                MatchupCompetitor.objects.create(**params)
            return instance

        def create_series(**kwargs):
            competitors = kwargs.pop("competitors", None) or self.competitors
            parent = kwargs.pop("parent", None)
            if parent:
                instance = create_instance(2, kwargs)
            else:
                instance = self.competition_details

            series_type = instance.series_type
            series_games = instance.series_games

            competitors_list = []
            matchups_left = math.floor(series_games / 2) if series_type == 1 else series_games
            for competitor in competitors:
                competitors_list.append({
                    "competitor": competitor,
                    "left": matchups_left
                })

            params = {"parent": instance, "competitors": competitors}
            for x in range(1, series_games + 1):
                params["child_num"] = x
                if series_type == 1 and x >= series_games / 2 + 1:
                    params["status"] = 5
                create_matchup(**params)

            return instance

        def create_tournament(**kwargs):
            competitors = kwargs.pop("competitors", None) or list(self.competitors)
            parent = kwargs.pop("parent", None)
            playoffs = kwargs.pop("playoffs", None)
            params = {}
            if parent:
                if playoffs:
                    competition = deepcopy(self)
                    competition.pk = None
                    competition.competition_type = 3
                    competition.status = 2
                    competition.parent = self
                    competition.save()
                    kwargs["competition"] = params['competition'] = competition
                instance = create_instance(3, kwargs)
            else:
                instance = self.competition_details
            params["parent"] = instance
            tourney_seeds = instance.tourney_seeds
            tourney_type = instance.tourney_type

            def create_round(current_ids, slots, round_num=1,
                             round_type=None, series_games=None, status=1):
                tourney_round = TourneyRound.objects.create(tournament=instance,
                                                            round_type=round_type,
                                                            round_num=round_num,
                                                            slots=slots
                                                            )
                new_round = []

                def base_slots(round_slot_count, round_count):
                    if round_count == 1:
                        return round_slot_count + ((total_matchups - 1) * (round_type - 1))
                    multiplier = 2 if round_type == 1 else ((round_count - 1) % 2) + 1
                    return round_slot_count + base_slots(round_slot_count * multiplier, round_count - 1)

                def tourney_positions(s, ls=None):
                    if ls is None:
                        ls = [0]
                    if len(ls) >= s:
                        return ls
                    current_slots = len(ls)
                    for pos in range(0, current_slots):
                        ls.insert(max(pos * 2, 1), current_slots * 2 - ls[pos * 2] - 1)
                    return tourney_positions(s, ls)

                half_slots = int(slots / 2)
                byes = slots - len(current_ids)
                round_byes = current_ids[0:byes]
                favorites = current_ids[byes:half_slots]
                underdogs = current_ids[half_slots:]
                slot_base = total_matchups * 2 - 2 + (round_num - tourney_rounds) if round_num > tourney_rounds else base_slots(half_slots, round_num) - half_slots
                if round_type == 2 and round_num % 2 == 0:
                    positions = tourney_positions(half_slots)
                    if round_num % 4 != 0:
                        positions = list(reversed(positions))
                else:
                    favorites = list(reversed(favorites))
                    positions = range(0, half_slots)

                for u, f in enumerate(positions):
                    if f >= byes:
                        child_num = slot_base + u + 1
                        f -= byes
                        u -= byes
                        if "dependent_id" in favorites[f]:
                            favorites[f]["dependent_outcome"] = 1
                            status = max(2, status)
                        if "dependent_id" in underdogs[u] and "dependent_outcome" not in underdogs[u]:
                            underdogs[u]["dependent_outcome"] = 1
                        if round_type == 2:
                            if round_num % 2 == 0:
                                favorites[f]["dependent_outcome"] = 2
                            if round_num == 1:
                                favorites[f]["dependent_outcome"] = 2
                                underdogs[u]["dependent_outcome"] = 2
                        if status == 5 and round_type == 1:
                            favorites[f]["dependent_outcome"] = 2

                        matchups = [favorites[f], underdogs[u]]
                        new_mc = {}

                        params.update({"tourney_round": tourney_round, "child_num": child_num,
                                       "competitors": matchups, "status": status})
                        if series_games:
                            params.update({"series_games": series_games,
                                           "series_type": 1})
                            new_instance = create_series(**params)
                            new_mc["dependent_type"] = 2
                        else:
                            new_instance = create_matchup(**params)
                            new_mc["dependent_type"] = 1

                        new_mc["dependent_id"] = new_instance.id
                        new_mc["left"] = matchups_left
                        new_round.append(new_mc)
                    else:
                        if "dependent_id" in round_byes[f] and round_type == 2:
                            round_byes[f]["dependent_outcome"] = 2

                return round_byes + new_round

            if tourney_seeds == 1:
                random.shuffle(competitors)

            tourney_rounds = math.ceil(math.log(len(competitors), 2))

            winners = []
            losers = []
            matchups_left = tourney_rounds - 1 + (tourney_type - 1) * (tourney_rounds + 1)
            for i, value in enumerate(competitors):
                mc = {"seed": i + 1}
                if type(value) == Competitor:
                    value.add_seed(i + 1)
                    mc["competitor"] = value
                else:
                    mc["dependent_id"] = value
                if playoffs:
                    mc["dependent_type"] = 4
                mc["left"] = matchups_left
                winners.append(mc)

            total_matchups = 2 ** tourney_rounds - 1

            for x in range(0, tourney_rounds):
                round_slots = 2 ** (tourney_rounds - x)
                byes = round_slots - len(winners)
                winners = create_round(winners, round_slots, round_num=x + 1, round_type=1)
                if tourney_type == 2:
                    round_num = x * 2
                    if x > 0:
                        losers = deepcopy(winners) + losers
                        losers = create_round(losers, round_slots, round_num=round_num, round_type=2)
                    else:
                        losers = deepcopy(winners[byes:])
                    if round_slots > 2:
                        losers = create_round(losers, int(round_slots / 2), round_num=round_num + 1, round_type=2)

            if tourney_type == 2:
                winners[0]["left"] = 0
                losers[0]["left"] = 1
                ids = create_round(winners + losers, 2, round_num=tourney_rounds + 1, round_type=1)
                ids[0]["left"] = 0
                create_round(ids + deepcopy(ids), 2, round_num=tourney_rounds + 2, round_type=1, status=5)

            return instance

        def create_season(**kwargs):
            competitors = kwargs.pop("competitors", None) or self.competitors
            parent = kwargs.pop("parent", None)
            if parent:
                instance = create_instance(4, kwargs)
            else:
                instance = self.competition_details

            num_competitors = len(competitors)
            season_type = instance.season_type
            if season_type == 2:
                season_games = instance.season_games
            else:
                rounds = instance.rounds
                instance.season_games = season_games = rounds * (num_competitors - 1)
                instance.save()
            playoff_format = instance.playoff_format

            competitor_list = []
            for c in competitors:
                mc = {"competitor": c,
                      "left": season_games}
                competitor_list.append(mc)

            competitors = competitor_list
            matchup_count = 1
            params = {"parent": instance}
            if season_type == 1:
                matchups = combinations(competitors, 2)

                for x in range(0, rounds):
                    for i, matchup in enumerate(matchups):
                        params["competitors"] = matchup
                        params["child_num"] = len(matchups) * x + i + 1
                        create_matchup(**params)
            else:
                for x in range(1, int(season_games / 2) + 1):
                    matchup_count = 1 if matchup_count == num_competitors else matchup_count

                    for i in range(0, num_competitors):
                        params["competitors"] = [competitors[i], competitors[(matchup_count + i) % num_competitors]]
                        params["child_num"] = ((x - 1) * num_competitors) + i + 1
                        create_matchup(**params)
                    matchup_count += 1

            if playoff_format:
                playoff_bids = instance.playoff_bids
                create_tournament(parent=instance, tourney_type=playoff_format, tourney_seeds=2,
                                  competitors=[instance.id] * playoff_bids, playoffs=True)

            return instance

        if self.status < 3:
            comp_type = self.competition_type
            if self.status == 1:
                if comp_type == 3:
                    self.competition_details.delete_matchups()
                else:
                    self.matchups.all().delete()
            pending_competitors = self.competitors.filter(status=0).all()
            if self.matchup_type == 2 and self.split_teams == 2:
                competitors = random.shuffle(list(pending_competitors))
                players_per_team = self.players_per_team
                num_teams = math.floor(len(competitors)/players_per_team)
                for i in range(0, num_teams):
                    team = competitors[i]
                    team.team_name = "Team {}".format(i)
                    team.status = 1
                    for x in range(1, players_per_team):
                        player = competitors[i * players_per_team + x]
                        team.players.add(player.player)
                        player.delete()
                    team.save()
                leftover = competitors[num_teams * players_per_team:]
                for i, c in enumerate(leftover):
                    team = competitors[i]
                    team.players.add(c.player)
                    c.delete()
            else:
                pending_competitors.delete()

            default_params = {"status": 1}
            if comp_type in range(1, 5):
                comp_funcs = [create_matchup, create_series, create_tournament, create_season]
                comp_funcs[comp_type - 1]()
            elif comp_type == 5:
                for child in self.children.all():
                    child.create_matchups()

            self.status = 1
            self.save()

    # Meta and String
    class Meta:
        verbose_name = _("Competition")
        verbose_name_plural = _("Competitions")
        ordering = ("name",)

    def __str__(self):
        return "{} {}".format(self.name, self.get_competition_type_display().title())


class Player(Model):
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE, related_name="player")
    rating = models.DecimalField(default=0, decimal_places=4, max_digits=5)
    favorite_game = models.ManyToManyField(Game, blank=True)

    @property
    def upcoming_matchups(self):
        return MatchupCompetitor.objects.filter(competitor__in=self.profile.competitors.all(),
                                                matchup__status__in=[1, 2]).order_by('matchup__date',
                                                                                     'matchup__child_num').all()
    @property
    def matchup_results(self):
        return MatchupCompetitor.objects.filter(competitor__in=self.profile.competitors.all(),
                                                matchup__status__in=[3, 4]).order_by('matchup__date',
                                                                                     'matchup__child_num').all()

    @property
    def wins(self):
        return MatchupCompetitor.objects.filter(competitor__in=self.profile.competitors.all(),
                                                place=1).count()

    @property
    def games_played(self):
        return MatchupCompetitor.objects.filter(competitor__in=self.profile.competitors.all(),
                                                matchup__status__in=[3, 4]).count()

    @property
    def win_perc(self):
        return round(self.wins / self.games_played, 3) * 100

    @property
    def record(self):
        return record_string(self.wins, self.games_played)

    @property
    def team_wins(self):
        teams = self.profile.competitors.filter(competitor_type=2)
        return MatchupCompetitor.objects.filter(competitor__in=teams, place=1).count()

    @property
    def team_games_played(self):
        teams = self.profile.competitors.filter(competitor_type=2)
        return MatchupCompetitor.objects.filter(competitor__in=teams, matchup__status__in=[3, 4]).count()

    @property
    def team_record(self):
        return record_string(self.team_wins, self.team_games_played)

    # Methods
    def get_absolute_url(self):
        return reverse('profile', kwargs={"pk": self.profile.id})

    def get_matchup_results(self, result_type="all", filter=None):
        competitors = self.profile.competitors
        if filter:
            competitors = competitors.filter(**filter)
        params = {"competitor__in": competitors}
        if result_type == "wins":
            params["place"] = 1
        results = MatchupCompetitor.objects.filter(**params)
        return results


class Competitor(Model):
    STATUS_TYPES = (
        (0, "pending"),
        (1, "verified")
    )
    team_name = models.CharField(max_length=30, validators=[RegexValidator(NAME_REGEX)], null=True, blank=True)
    competitor_type = models.IntegerField(choices=constants.MATCHUP_TYPES, default=1)
    competition = models.ForeignKey(Competition, on_delete=models.CASCADE, related_name="competitor_set")
    captain = models.ForeignKey(Profile, related_name="competition_team_captain", null=True)
    players = models.ManyToManyField(Profile, related_name="competitors")
    team = models.ForeignKey(Team, related_name="team_competitors", null=True, blank=True)
    status = models.IntegerField(choices=STATUS_TYPES, default=1)

    invitees = models.ManyToManyField(Profile, related_name="team_competition_invites", through="CompetitionInvite")

    @property
    def player(self):
        return self.players.first() if self.competitor_type == 1 else False

    @property
    def profile_image(self):
        player = self.player
        if player:
            return player.profile_image
        elif self.team:
            return self.team.profile_image
        return "/static/svg/profile_team.png"

    @property
    def name(self):
        return "{}".format(self.team or self.team_name or self.captain)

    @property
    def upcoming_matchups(self):
        return self.matchup_competitors.filter(matchup__status__in=[1, 2]).order_by('matchup__date',
                                                                                    'matchup__child_num').all()

    @property
    def matchup_results(self):
        return self.matchup_competitors.filter(matchup__status__in=[3, 4]).order_by('matchup__date',
                                                                                    'matchup__child_num').all()

    @property
    def wins(self):
        return self.matchup_competitors.filter(place=1).count()

    @property
    def games_played(self):
        return self.matchup_competitors.filter(matchup__status=3).count()

    @property
    def record(self):
        return record_string(self.wins, self.games_played)

    def seed(self, competition=None):
        seed = self.seeds.filter(competition=(competition or self.competition))
        if seed.exists():
            return seed.first().seed

    # Methods
    def get_absolute_url(self):
        return reverse('competitor', kwargs={"pk": self.id})

    def add_seed(self, seed, competition=None):
        competition = competition or self.competition
        obj, created = CompetitorSeed.objects.get_or_create(competition=competition, competitor=self)
        obj.seed = seed
        obj.save()

    class Meta:
        unique_together = (
            ("competition", "team"),
        )

    def __str__(self):
        return "{} in {}".format(self.name, self.competition)


class CompetitorSeed(Model):
    competitor = models.ForeignKey(Competitor, on_delete=models.CASCADE, related_name="seeds")
    competition = models.ForeignKey(Competition, on_delete=models.CASCADE, related_name="seeds")
    seed = models.IntegerField(default=1)

    class Meta:
        unique_together = ("competition", "competitor")


class Season(Model):
    competition = models.ForeignKey(Competition, on_delete=models.CASCADE)
    season_type = models.IntegerField(choices=constants.SEASON_TYPES)
    season_games = models.IntegerField(choices=constants.SEASON_GAMES, null=True, blank=True)
    rounds = models.IntegerField(choices=((x, x) for x in range(1, 11)), null=True, blank=True)
    playoff_format = models.IntegerField(choices=constants.TOURNEY_TYPES, null=True, blank=True)
    playoff_bids = models.IntegerField(choices=constants.PLAYOFF_BIDS, null=True, blank=True)
    status = models.IntegerField(choices=constants.STATUS_TYPES, default=0)

    @property
    def name(self):
        value = "Round Robin" if self.season_type == 1 else "Game Season"
        return "{} {}".format(self.season_games, value)

    @property
    def matchups(self):
        return Matchup.objects.filter(parent_type=4, parent_id=self.id).all()

    @property
    def playoff(self):
        if self.playoff_format:
            return self.competition.children.first().competiton_details
        return False

    @property
    def results(self):
        matchups = self.matchups
        mcs = MatchupCompetitor.objects.filter(matchup__in=matchups) \
            .values("competitor") \
            .annotate(
                wins=Sum(
                    Case(
                        When(place=1, matchup__status__in=[3, 4], then=1),
                        default=0,
                        output_field=models.IntegerField(),
                    )
                ),
                games=Sum(
                    Case(
                        When(matchup__status__in=[3, 4], then=1),
                        default=0,
                        output_field=models.IntegerField(),
                    )
                )
            ).order_by()
        mcs = mcs.annotate(
                win_perc=Case(When(games=0, then=0),
                              default=F('wins') / F('games'),
                              output_field=models.DecimalField(decimal_places=3)
                              )
            ).order_by('-win_perc')
        finished = not matchups.exclude(status__in=[3, 4]).exists()
        standings = []
        place = 1
        for i, c in enumerate(mcs):
            gb = 0
            if i > 0:
                wins = standings[0]["wins"]
                gp = standings[0]["games"]
                loses = gp - wins
                gb = ((wins - c["wins"]) + (c["games"] - c["wins"] - loses))/2
                if gb > standings[i - 1]["games back"]:
                    place = i + 1
            line = OrderedDict()
            line["competitor"] = Competitor.objects.get(id=c["competitor"])
            line["wins"] = c["wins"]
            line["games"] = c["games"]
            line["games back"] = gb
            line["win %"] = 0 if c["games"] == 0 else round(c["wins"] / c["games"], 3) * 100
            line["place"] = place
            standings.append(deepcopy(line))

        playoff = self.playoff
        if playoff:
            finished, playoff_results = playoff.results
            if finished:
                standings = playoff_results + standings[self.playoff_bids:]
        return finished, standings

    @property
    def winner(self):
        finished, standings = self.results
        if finished:
            return self.standings[0]
        return False

    def get_absolute_url(self):
        self.competition.get_absolute_url()

    def update_status(self, matchup=None):
        status = self.status
        parent = self.competition
        finished, results = self.results
        if finished:
            status = 4
            if self.playoff_format:
                status = 3
                self.playoff.update_status()
                playoff_competitors = results[:self.playoff_bids]
                for seed, c in enumerate(playoff_competitors):
                    mc = get_object_or_404(MatchupCompetitor,
                                           dependent_id=self.id,
                                           dependent_type=4,
                                           seed=seed + 1)
                    mc.competitor = c["competitor"]
        status = 1 if status == 2 else (3 if status != 4 else status)
        self.status = status
        self.save()
        parent.update_status()

    def __str__(self):
        return "{} {}".format(self.competition.name, self.name)


class Tournament(Model):
    competition = models.ForeignKey(Competition, on_delete=models.CASCADE)
    tourney_type = models.IntegerField(choices=constants.TOURNEY_TYPES)
    tourney_seeds = models.IntegerField(choices=constants.TOURNEY_SEEDS)
    status = models.IntegerField(choices=constants.STATUS_TYPES, default=0)

    @property
    def name(self):
        value = "Playoff" if self.competition.competition_type == 4 else "Tournament"
        return "{} {}".format(self.get_tourney_type_display().title(), value)

    @property
    def matchups(self):
        return Matchup.objects.filter(parent_type=3, parent_id=self.id).all()

    @property
    def season(self):
        parent = self.competition.parent
        if parent:
            return parent.competition_details
        return False

    @property
    def final_matchup(self):
        tourney_rounds = math.ceil(math.log(self.competition.competitors.count(), 2))
        if self.tourney_type == 2:
            tourney_rounds += 2
        final_round = self.tourney_rounds.filter(round_type=1, round_num=tourney_rounds)
        if final_round.exists():
            if self.tourney_type == 3:
                series = final_round.first().tourney_series.first()
                matchups = series.matchups.filter(status__in=[3, 4]).order_by("child_num")
                return matchups[0]
            else:
                matchup = final_round.first().tourney_matchups.first()
                if self.tourney_type == 2 and matchup.status == 6:
                    final_round = self.tourney_rounds.filter(round_type=1, round_num=tourney_rounds - 1).first()
                    matchup = final_round.first().tourney_matchups.first()
                if matchup.status in [3, 4]:
                    return matchup
        return False

    @property
    def winner(self):
        final_matchup = self.final_matchup
        if final_matchup:
            return final_matchup.winner
        return False

    @property
    def results(self):
        tourney_rounds = math.ceil(math.log(self.competition.competitors.count(), 2))
        final = self.final_matchup
        standings = []
        if final:
            finished, final_results = final.results
            standings.append(final_results[0])
            standings.append(final_results[1])
        if self.tourney_type == 2:
            loser_rounds = (tourney_rounds - 1) * 2
            for x in range(0, loser_rounds):
                tourney_round = self.tourney_rounds.get(round_type=2, round_num=loser_rounds - x)
                losers = tourney_round.get_losers()
                for loser in losers:
                    line = OrderedDict()
                    standings.append(line.update({"competitor": loser,
                                                  "place": x + 3}))
        else:
            for x in range(0, tourney_rounds - 1):
                tourney_round = self.tourney_rounds.get(round_type=2, round_num=tourney_rounds - 1 - x)
                losers = tourney_round.get_losers()
                for loser in losers:
                    line = OrderedDict()
                    standings.append(deepcopy(line.update({"competitor": loser,
                                                           "place": x + 3})))
        return bool(final), standings

    def get_absolute_url(self):
        self.competition.get_absolute_url()

    def update_status(self, matchup=None):
        status = self.status
        parent = self.competition
        finished, results = self.results
        if finished:
            status = 4
            season = self.season
            if season:
                season.status = 4
                season.save()
        status = 1 if status == 2 else (3 if status != 4 else status)
        self.status = status
        self.save()
        parent.update_status()

    def delete_matchups(self):
        self.tourney_rounds.all().delete()

    def __str__(self):
        return "{} {}".format(self.competition.name, self.name)


class TourneyRound(Model):
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, related_name="tourney_rounds")
    round_type = models.IntegerField(choices=((1, "winner"), (2, "loser")), null=True)
    round_num = models.IntegerField(null=True)
    slots = models.IntegerField(null=True)

    @property
    def name(self):
        value = "Round {}".format(self.round_num)
        if self.tournament.tourney_type == 2:
            value = "{}'s {}".format(self.get_round_type_display().title(), value)
        return value

    def get_losers(self):
        if self.tournament.tourney_type != 3:
            finished_matchups = self.tourney_matchups.filter(status__in=[3, 4])
            return Competitor.objects.filter(
                id__in=MatchupCompetitor.objects.filter(
                    matchup__in=finished_matchups,
                    place=2).values_list("competitor")
            )
        else:
            finished_series = self.tourney_series.filter(status__in=[3, 4])
            losers = []
            for series in finished_series:
                losers.append(series.results[1].competitor)
            return losers

    def __str__(self):
        return "{} {}".format(self.tournament, self.name)


class Series(Model):
    competition = models.ForeignKey(Competition, on_delete=models.CASCADE)
    series_type = models.IntegerField(choices=constants.SERIES_TYPES)
    series_games = models.IntegerField(choices=constants.SERIES_GAMES)
    status = models.IntegerField(choices=constants.STATUS_TYPES, default=0)
    tourney_round = models.ForeignKey(TourneyRound, null=True, blank=True, related_name="tourney_series")
    child_num = models.IntegerField(default=1)

    @property
    def name(self):
        if self.series_type == 3:
            value = "{} Game Series".format(self.series_games)
        else:
            value = "{} {} Series".format(self.get_series_type_display().title(), self.series_games)
        return value

    @property
    def matchups(self):
        return Matchup.objects.filter(parent_type=2, parent_id=self.id).all()

    @property
    def min_games(self):
        return math.ceil(self.series_games / 2) if self.series_type == 1 else self.series_games

    @property
    def results(self):
        finished_matchups = self.matchups.filter(status__in=[3, 4])
        mcs = MatchupCompetitor.objects.filter(matchup__in=finished_matchups)\
            .values("competitor")\
            .annotate(
                wins=Sum(
                        Case(
                            When(place=1, then=1),
                            default=0,
                            output_field=models.IntegerField(),
                        )
                    )
            ).order_by('-wins')
        finished = (finished_matchups.count() if self.series_type == 3 else mcs[0].wins) >= self.min_games
        standings = []
        place = 1
        for i, c in enumerate(mcs):
            if i > 0 and c.wins < standings[i - 1]["wins"]:
                place = i + 1
            line = OrderedDict()
            line.update({"competitor": Competitor.objects.get(id=c.competitor),
                         "wins": c.wins,
                         "place": place})
            standings.append(deepcopy(line))
        return finished, standings

    @property
    def winner(self):
        finished, results = self.results
        if finished:
            return results[0].competitor
        return False

    def get_absolute_url(self):
        self.competition.get_absolute_url()

    def update_status(self, matchup):
        status = self.status
        parent = self.competition
        finished, results = self.results
        if finished:
            winner = results[0]["competitor"]
            status = 4
            matchups = self.matchups.filter(child_num__gt=matchup.child_num)
            if matchups.exists():
                for m in matchups:
                    m.status = 6
                    m.save()
            if self.tourney_round:
                params = {
                    "dependent_outcome": 1,
                    "dependent_type": 2,
                    "dependent_id": self.id
                }
                dependents = MatchupCompetitor.objects.filter(**params)
                if dependents.exists():
                    for dependent in dependents:
                        dependent.matchup.update_status()
                        dependent.competitor = winner
                        dependent.seed = winner.seed()
                        dependent.save()
                parent = self.tourney_round.tournament
        elif self.series_type != 3:
            status = 3
            necessary_games = self.min_games - results[0]["wins"] + self.matchups.filter(status__in=[3, 4]).count()
            new_matchup, created = Matchup.objects.get_or_create(competition=self.competition,
                                                                 parent_id=self.id,
                                                                 parent_type=2,
                                                                 child_num=necessary_games)
            new_matchup.status = 1
            new_matchup.save()
            if created:
                for mc in matchup.mc_set.all():
                    mc.pk = None
                    mc.matchup = new_matchup
                    mc.save()
            if self.tourney_round:
                parent = self.tourney_round.tournament
        status = 1 if status == 2 else (3 if status != 4 else status)
        self.status = status
        self.save()
        parent.update_status()

    # Meta and String
    class Meta:
        verbose_name = _("Series")
        verbose_name_plural = _("Series")
        ordering = ("competition",)

    def __str__(self):
        return "{} {}".format(self.competition.name, self.name)


class Matchup(Model):
    competition = models.ForeignKey(Competition, on_delete=models.CASCADE, related_name="matchups")
    parent_type = models.IntegerField(choices=constants.COMPETITION_TYPES, null=True, editable=False)
    parent_id = models.IntegerField(null=True, editable=False)
    date = models.DateField(null=True, blank=True)
    time = models.TimeField(null=True, blank=True)
    venue = models.ForeignKey(GameVenue, null=True, blank=True)
    notes = models.CharField(max_length=500, null=True, blank=True)
    witness = models.ForeignKey(Profile, null=True, blank=True, related_name="witness")
    child_num = models.IntegerField(default=1)
    status = models.IntegerField(choices=constants.STATUS_TYPES, default=0)
    tourney_round = models.ForeignKey(TourneyRound, null=True, blank=True,
                                      related_name="tourney_matchups", on_delete=models.CASCADE)
    competitors = models.ManyToManyField(Competitor, through='MatchupCompetitor',
                                         through_fields=('matchup', 'competitor'),
                                         related_name="matchups")
    objects = managers.MatchupManager()

    @property
    def name(self):
        if self.parent_type in [2, 3, 4]:
            if self.parent_type == 3:
                parent = self.tourney_round
            else:
                parent = self.parent
            return "{} Matchup {}".format(parent, self.child_num)
        return "{}".format(self.competition)

    @property
    def parent(self):
        if self.parent_type == 2:
            return Series.objects.get(id=self.parent_id)
        elif self.parent_type == 3:
            return Tournament.objects.get(id=self.parent_id)
        elif self.parent_type == 4:
            return Season.objects.get(id=self.parent_id)

    @property
    def matchup_type(self):
        return self.competition.matchup_type

    @property
    def date_formatted(self):
        if self.date:
            return self.date.strftime('%A %b %-d, %Y')
        return self.competition.date_formatted

    @property
    def time_formatted(self):
        if self.time:
            return self.time.strftime('%-I:%M %p')
        return self.competition.time_formatted

    @property
    def competition_competitors(self):
        return self.competition.competitors

    @property
    def creator(self):
        return self.competition.creator

    @property
    def game_type(self):
        return self.competition.game_type

    @property
    def winner(self):
        if self.status in [3, 4]:
            winner = self.mc_set.filter(place=1)
            if winner.exists():
                return winner.get().competitor
        return False

    @property
    def results(self):
        finished = self.status in [3, 4]
        mcs = self.mc_set.values("competitor", "place").order_by("place")
        standings = []
        for i, c in enumerate(mcs):
            line = OrderedDict()
            line.update({"competitor": Competitor.objects.get(id=c.competitor),
                         "place": c.place})
            standings.append(deepcopy(line))
        return finished, standings

    # methods
    def get_absolute_url(self):
        return reverse('matchup', kwargs={"pk": self.pk})

    def set_parent(self, parent):
        if parent:
            parent_name = type(parent).__name__.lower()
            for value, key in constants.COMPETITION_TYPES:
                if parent_name == key:
                    self.parent_type = value
            self.parent_id = parent.pk
            self.save()

    def update_status(self):
        status = self.status
        status = 1 if status == 2 else 3
        self.status = status
        self.save()
        parent = self.parent or self.competition
        parent.update_status(self)

    # Meta and String
    class Meta:
        verbose_name = _("Matchup")
        verbose_name_plural = _("Matchups")
        ordering = ("competition", "child_num")

    def __str__(self):
        if self.parent_type in [2, 3, 4]:
            return "{} {}".format(self.competition, self.name)
        return "{}".format(self.competition)


class MatchupCompetitor(Model):
    matchup = models.ForeignKey(Matchup, on_delete=models.CASCADE, related_name="mc_set")
    competitor = models.ForeignKey(Competitor, null=True, blank=True, related_name="matchup_competitors")
    dependent_outcome = models.IntegerField(null=True, choices=((1, "winner"), (2, "loser")))
    dependent_type = models.IntegerField(null=True, choices=((1, "matchup"), (2, "series"), (4, "season")))
    dependent_id = models.IntegerField(null=True)
    notes = models.CharField(max_length=500, null=True, blank=True)
    seed = models.IntegerField(default=1)
    place = models.IntegerField(null=True, blank=True)
    left = models.IntegerField(default=0)

    @property
    def dependent_text(self):
        return "{} of {}".format(self.get_dependent_outcome_display().title(), self.dependent)

    @property
    def opponents(self):
        return self.matchup.competitors.exclude(id=self.competitor.id)

    @property
    def profile_image(self):
        if self.matchup.matchup_type == 1:
            return "/static/svg/profile_inv.png"
        else:
            return "/static/svg/profile_team.png"

    @property
    def place_string(self):
        last_digit = int(str(self.place)[-1])
        endings = {1: "st", 2: "nd", 3: "rd"}
        ending = endings[last_digit] \
            if self.place not in range(11, 14) and last_digit in endings \
            else "th"
        return "{}{}".format(self.place, ending)

    @property
    def dependent(self):
        if self.dependent_type == 1:
            return Matchup.objects.get(id=self.dependent_id)
        elif self.dependent_type == 2:
            return Series.objects.get(id=self.dependent_id)
        elif self.dependent_type == 4:
            return Season.objects.get(id=self.dependent_id)

    # methods
    def get_absolute_url(self):
        if self.competitor:
            return self.competitor.get_absolute_url()
        else:
            return self.dependent.get_absolute_url()

    def update_status(self, final=True):
        params = {
            "dependent_outcome": self.place,
            "dependent_type": 1,
            "dependent_id": self.matchup.id
        }
        if self.place == 1 and final:
            self.matchup.update_status()
        else:
            dependent = MatchupCompetitor.objects.filter(**params)
            if dependent.exists():
                dependent = dependent.first()
                if dependent.matchup.status != 4:
                    dependent.matchup.status = 1
                    dependent.matchup.save()
                    dependent.competitor = self.competitor
                    dependent.seed = self.seed
                    dependent.left = min(dependent.left, self.left - 1 if self.place == 1 else 0)
                    dependent.save()
                    if not dependent.matchup.mc_set.filter(competitor__isnull=True).exists():
                        dependent.matchup.status = 1
                        dependent.matchup.save()
        dependent = self.dependent
        if dependent and self.dependent_type == 1:
            dependent.status = 4
            dependent.save()

    # Meta and String
    class Meta:
        unique_together = (
            ("matchup", "competitor"),
            ("dependent_outcome", "dependent_type", "dependent_id", "seed")
        )
        verbose_name = _("Matchup Competitor")
        verbose_name_plural = _("Matchup Competitors")
        ordering = ("matchup__competition", "matchup__date", "matchup__child_num", "seed")

    def __str__(self):
        return "{}".format(self.competitor or self.dependent_text)


class StatMember(Model):
    parent_id = models.IntegerField()
    parent_type = models.IntegerField(choices=((k, v) for k, v in enumerate(managers.StatMemberManager.PARENT_TYPES)))
    child_id = models.IntegerField()
    child_type = models.IntegerField(choices=((k, v) for k, v in enumerate(managers.StatMemberManager.CHILD_TYPES)))

    objects = managers.StatMemberManager()

    class Meta:
        unique_together = ("parent_id", "parent_type", "child_id", "child_type")

    @property
    def parent(self):
        class_name = self.get_parent_type_display()
        return getattr(sys.modules[__name__], class_name).objects.get(id=self.parent_id)

    @property
    def child(self):
        class_name = self.get_child_type_display()
        return getattr(sys.modules[__name__], class_name).objects.get(id=self.child_id)

    def __str__(self):
        return "{} {}".format(self.parent, self.child)


class BoxStat(Model):
    stat_member = models.ForeignKey(StatMember, on_delete=models.CASCADE)
    stat_name = models.CharField(max_length=30)
    stat_value = models.DecimalField(decimal_places=2, max_digits=10)
    added_by = models.ForeignKey(Profile)
    verified = models.BooleanField(default=False)

    def __str__(self):
        return "{} - {}".format(self.stat_member, self.stat_name)

    class Meta:
        unique_together = (("stat_member", "stat_name", "added_by"),)


class CompetitionInvite(Model):
    INVITE_TYPES = ((1, "competition"), (2, "team"), (3, "open"))
    INVITE_MODEL = Competition
    PROFILE_MODEL = Profile

    competition = models.ForeignKey(Competition, on_delete=models.CASCADE, related_name="invites")
    player = models.ForeignKey(PROFILE_MODEL, null=True, blank=True, related_name="competition_invites")
    competitor = models.ForeignKey(Competitor, null=True, blank=True, related_name="competitor_invites")
    invite = models.ForeignKey(Invitation, null=True, blank=True, related_name="pending_invites")
    expiration = models.DateTimeField(null=True, blank=True)
    invite_type = models.IntegerField(choices=INVITE_TYPES, default=1)
    approved = models.BooleanField(default=False)
    accepted = models.BooleanField(default=False)
    creation_datetime = models.DateTimeField(auto_now_add=True, editable=False, null=True)

    @property
    def status(self):
        if self.approved:
            return "approved"
        if self.accepted:
            return "accepted"
        return "pending"

    # Methods
    def get_absolute_url(self):
        return reverse(self.INVITE_MODEL.__name__.lower(),
                       kwargs={"pk": self.competition.id}) + "invite/{}/".format(self.pk)

    def approve(self):
        if self.accepted:
            self.competition.add_competitor(invite=self)
        else:
            self.approved = True
            self.save()

    def accept(self):
        if self.approved:
            self.competition.add_competitor(invite=self)
        else:
            self.accepted = True
            self.save()

    def __str__(self):
        return str(self.player) or self.invite.email

    class Meta:
        unique_together = ("competition", "player")


class CompetitionSignUpPage(models.Model):
    competition = models.OneToOneField(Competition, on_delete=models.CASCADE, related_name="signup_page")
    verification_key = models.CharField(max_length=40, primary_key=True)
    expiration = models.DateTimeField(null=True, blank=True)
    msg_image = models.ImageField(upload_to=upload_to_path, null=True, blank=True)

    @property
    def creator(self):
        return self.competition.creator

    @property
    def image(self):
        if self.msg_image:
            return self.msg_image.url
        return "/svg/profile_competition.png"

    # Methods
    def get_absolute_url(self):
        return reverse('competition_signup', kwargs={"pk": self.competition.id, "key": self.pk})

    def key_expired(self):
        if self.expiration:
            return self.expiration <= timezone.now()
        return False

    def __str__(self):
        return "{} Sign Up".format(self.competition)


def place_string(place):
    last_digit = int(str(place)[-1])
    endings = {1: "st", 2: "nd", 3: "rd"}
    ending = endings[last_digit] \
        if place not in range(11, 14) and last_digit in endings \
        else "th"
    return "{}{}".format(place, ending)


from django.dispatch import receiver
from django.utils import timezone
from django.db.models.signals import post_save
from invitations.signals import invite_accepted


@receiver(invite_accepted, sender=Invitation)
def invite_accepted(sender, email, **kwargs):
    invitations = Invitation.objects.filter(email=email).values_list("id", flat=True)

    profile = User.objects.get(email=email).profile
    CompetitionInvite.objects.filter(invite__in=invitations).update(player=profile)
    LeagueInvite.objects.filter(invite__in=invitations).update(player=profile)


@receiver(post_save, sender=Profile)
def create_player_for_profile(sender, created, instance, **kwargs):
    if created:
        Player.objects.create(profile=instance)


@receiver(post_save, sender=CompetitionInvite)
def send_competition_invite(sender, created, instance, **kwargs):
    profile = instance.player
    if created and profile:
        params = {
            "user": profile.user,
            "subject": "You're Invited!",
            "template": "emails/invitation.html",
            "object_type": "competition",
            "instance": instance.competitor or instance.competition
        }
        send_notification(**params)

