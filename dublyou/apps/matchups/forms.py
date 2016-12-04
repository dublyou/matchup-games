from django import forms
from ...constants import COMP_TYPES, EVENT_TYPES, SPLIT_TEAMS, SERIES_TYPES, TOURNEY_TYPES, TOURNEY_SEEDS, SEASON_TYPES
from ...forms import MyBaseForm
from ..leagues.models import League
from django.core.validators import EmailValidator
from . import models
from . import fields
import math
import random

# from django.utils.translation import ugettext_lazy as _

INPUT_CRITERIA = {
    "event_type": range(1, 5),
    "name": r"^[-\s\.\w\d]{1,30}$",
    "comp_type": range(1, 3),
    "players_per_team": range(2, 33),
    "split_teams": range(1, 3),
    "league": r"^[-\s\.\w\d]{1,30}$",
    "series_games": range(3, 16, 2),
    "tourney_type": range(1, 3),
    "tourney_seeds": range(1, 3),
    "season_scheduling_type": range(1, 3),
    "round_robin": range(1, 11),
    "season_games": range(2, 163, 2),
    "playoff_bids": range(2, 33),
    "playoff_format": {1, 2, "series"},
    "num_events": range(2, 17),
    "game_rules": r"^[-\n\s\.\w\d]{1,300}$",
    "game_location": "^[-\s\.\w\d]{1,30}$",
}


class CreateGameForm(MyBaseForm):
    event_type = forms.ChoiceField(choices=EVENT_TYPES)
    event_name = forms.CharField(required=False, max_length=50)
    game_type = fields.GameField(required=False)
    competitors_by = forms.ChoiceField(choices=((1, "assigned"), (2, "league")))
    league = forms.CharField(required=False, max_length=50)
    comp_type = forms.ChoiceField(label="Competitor Type", choices=COMP_TYPES)
    split_teams = forms.ChoiceField(choices=SPLIT_TEAMS, required=False)
    players_per_team = forms.IntegerField(min_value=2, max_value=32, required=False)
    series_type = forms.ChoiceField(choices=SERIES_TYPES)
    series_games = forms.IntegerField(min_value=2, max_value=15, required=False)
    tourney_type = forms.ChoiceField(choices=TOURNEY_TYPES, required=False)
    tourney_seeds = forms.ChoiceField(choices=TOURNEY_SEEDS, required=False)
    season_type = forms.ChoiceField(choices=SEASON_TYPES, required=False)
    season_games = forms.IntegerField(min_value=1, max_value=162, required=False)
    season_playoffs = forms.BooleanField(required=False)
    playoff_bids = forms.IntegerField(min_value=2, max_value=32, required=False)
    playoff_format = forms.ChoiceField(choices=TOURNEY_TYPES, required=False)

    instance = None

    def __init__(self, *args, **kwargs):
        if "competitors" in kwargs:
            self.competitors = kwargs.pop('competitors')

        if "user" in kwargs:
            self.user = kwargs.pop('user')

        super(CreateGameForm, self).__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super(CreateGameForm, self).clean()

        if cleaned_data["competitors_by"] == 2:
            try:
                self.league = League.objects.get(league_name=cleaned_data["league"])
            except League.DoesNotExist:
                self.add_error("league", forms.ValidationError(message="League does not exist", code="invalid"))
        else:
            self.league = None
        # clean event_type dependent inputs

        dependent_inputs = [{"name": "event_type",
                             "fields": {1: ["game_type"],
                                        2: ["game_type", "series_type", "series_games"],
                                        3: ["game_type", "tourney_type", "tourney_seeds"],
                                        4: ["game_type", "season_type", "season_games",
                                            {"name": "season_playoffs",
                                             "fields": {True: ["playoff_bids", "playoff_format"],
                                                        False: []
                                                        }
                                             }
                                            ],
                                        5: []
                                        }
                             },
                            {"name": "competitors_by",
                             "fields": {1: [{"name": "comp_type",
                                             "fields": {1: [],
                                                        2: ["split_teams", "players_per_team"]
                                                        }
                                             }
                                            ],
                                        2: ["league"]
                                        }
                             }
                            ]

        for input_tree in dependent_inputs:
            self.clean_dependent_inputs(input_tree, INPUT_CRITERIA)

    def set_competitors(self, league=None):
        self.league = league or self.league
        if self.league.comp_type == 1:
            self.competitors = league.league_members.all()
        elif self.league.comp_type == 2:
            self.competitors == league.team_set.all()

    def _create_game(self, parent_event, child_num=1, matchups=None,
                     tourney_round=None):
        game = models.Game.objects.create(parent_event=parent_event,
                                          child_num=child_num,
                                          tourney_round=tourney_round)

        matchups = matchups or self.competitors

        matchup = models.Matchup(game=game) if self.cleaned_data["comp_type"] == 1 else models.TeamMatchup(game=game)

        for m in matchups:
            if tourney_round:
                if "type" in m:
                    matchup.dependent_type = m["type"]
                    if m["type"] == 3:
                        matchup.dependent_series = m["id"]
                    else:
                        matchup.dependent_game = m["id"]
                else:
                    matchup.seed = m["seed"]
                    matchup.competitor = m["id"]

            else:
                matchup.competitor = m

            matchup.save()

        return game

    def _create_series(self, parent_event=None, series_type=None, series_games=None,
                       competitors=None, child_num=1, tourney_round=None):
        series_type = series_type or self.cleaned_data.get("series_type")
        series_games = series_games or self.cleaned_data.get("series_games")

        if parent_event:
            instance = models.GameEvent(event_type=self.cleaned_data["event_type"],
                                        game_type=self.cleaned_data["game_type"],
                                        comp_type=self.cleaned_data["comp_type"],
                                        num_children=series_games,
                                        parent_event=parent_event,
                                        child_num=child_num
                                        )
        else:
            instance = self.instance
            instance.num_children = series_games

        instance.save()

        models.Series.objects.create(event=instance,
                                     series_type=series_type,
                                     series_games=series_games,
                                     tourney_round=tourney_round)

        competitors = competitors or self.competitors

        for x in range(1, series_games + 1):
            self._create_game(instance, child_num=x, matchups=competitors)

        return instance

    def _create_round(self, event, tournament, current_ids, round_slots,
                      round_num=1, dependent_type=None, series_games=None):
        tourney_round = models.TourneyRound.objects.create(tournament=tournament,
                                                           round_type=1,
                                                           round_num=round_num)

        ids = []
        round_games = len(current_ids)

        for y in range(0, round_games):
            favorite_seed = int((round_slots / 2) - (round_games - y) + 1)
            underdog_seed = (round_slots + 1) - favorite_seed
            matchups = [current_ids[favorite_seed], current_ids[underdog_seed]]
            if series_games:
                new_id = self._create_series(event, child_num=y + 1, competitors=matchups,
                                             series_games=series_games, series_type=1, tourney_round=tourney_round)
            else:
                new_id = self._create_game(event, child_num=y + 1, matchups=matchups, tourney_round=tourney_round)
            ids = [{"id": new_id, "type": dependent_type}] + ids
        return ids

    def _create_tournament(self, parent_event=None, tourney_type=None,
                           tourney_seeds=None, competitors=None, child_num=1):
        if competitors:
            num_competitors = len(competitors)
        else:
            num_competitors = len(self.competitors)
            competitors = self.competitors

        tourney_rounds = math.ceil(math.log(num_competitors, 2))
        tourney_seeds = tourney_seeds or self.cleaned_data.get("tourney_seeds")
        tourney_type = tourney_type or self.cleaned_data.get("tourney_type")

        games = ((2 ** tourney_rounds) - 1) * tourney_type
        if parent_event:
            instance = models.GameEvent(event_type=self.cleaned_data["event_type"],
                                        game_type=self.cleaned_data["game_type"],
                                        comp_type=self.cleaned_data["comp_type"],
                                        num_children=games,
                                        parent_event=parent_event,
                                        child_num=child_num
                                        )
        else:
            instance = self.instance
            instance.num_children = games

        instance.save()

        tournament = models.Tournament.objects.create(event=instance,
                                                      tourney_type=tourney_type,
                                                      tourney_seeds=tourney_seeds)

        if tourney_seeds == 1:
            random.shuffle(competitors)

        round1_byes = (2 ** (tourney_rounds - 1)) - num_competitors

        bye_ids = []
        ids = []
        l_ids = []
        for i, competitor in enumerate(competitors):
            if i < round1_byes:
                bye_ids.append({"id": competitor})
            else:
                ids.append({"id": competitor})

        for x in range(0, tourney_rounds):

            round_slots = 2 ** (tourney_rounds - x - 1)

            ids = self._create_round(event=instance, tournament=tournament, current_ids=ids,
                                     round_slots=round_slots, round_num=x+1, dependent_type=None)
            if tourney_type == 2:
                if x == 0:

                    round1_byes = int(round_slots/2) - len(ids)
                    l_bye_ids = []
                    for i, l_id in enumerate(l_ids):
                        if i < round1_byes:
                            l_bye_ids.append({"id": l_id, "type": 2})
                        else:
                            l_ids.append({"id": l_id, "type": 2})

                    round_slots = int(round_slots/2)

                    l_ids = self._create_round(event=instance, tournament=tournament, current_ids=l_ids,
                                               round_slots=round_slots, round_num=1, dependent_type=2)

                    l_ids = l_bye_ids + l_ids
                else:
                    round_num = x * 2
                    l_ids = ids + l_ids
                    l_ids = self._create_round(event=instance, tournament=tournament, current_ids=l_ids,
                                               round_slots=round_slots, round_num=round_num, dependent_type=2)

                    l_ids = self._create_round(event=instance, tournament=tournament, current_ids=l_ids,
                                               round_slots=round_slots, round_num=round_num + 1, dependent_type=2)

            if x == 0:
                ids = bye_ids + ids

        return instance

    def _create_season(self, parent_event=None, season_type=None, season_games=None, competitors=None,
                       season_playoffs=None, playoff_bids=None, playoff_format=None, child_num=1):
        season_type = season_type or self.cleaned_data.get("season_type")
        season_games = season_games or self.cleaned_data.get("season_games")

        if competitors:
            num_competitors = len(competitors)
        else:
            num_competitors = len(self.competitors)
            competitors = self.competitors

        games = season_games * num_competitors if season_type == 1 else season_games

        if parent_event:
            instance = models.GameEvent(event_type=self.cleaned_data["event_type"],
                                        game_type=self.cleaned_data["game_type"],
                                        comp_type=self.cleaned_data["comp_type"],
                                        num_children=games,
                                        parent_event=parent_event,
                                        child_num=child_num
                                        )
        else:
            instance = self.instance
            instance.num_children = games

        instance.save()

        models.Tournament.objects.create(event=instance,
                                         season_type=season_type,
                                         season_games=season_games,
                                         season_playoffs=False)

        matchup_count = 1

        if season_type == 1:
            for r in range(0, season_games):
                for i in range(0, num_competitors):
                    for x in range(i + 1, num_competitors):
                        game_competitors = [competitors[i], competitors[x]]
                        child_num = (r * i) + (i * (x - i + 2)) + x - i + 2
                        self._create_game(instance, matchups=game_competitors, child_num=child_num)
        else:
            for x in range(1, int(season_games / 2) + 1):
                matchup_count = 1 if matchup_count == num_competitors else matchup_count

                for i in range(0, num_competitors):
                    opp_i = (matchup_count + i) % num_competitors
                    game_competitors = [competitors[i], competitors[opp_i]]
                    child_num = ((x - 1) * num_competitors) + i + 1
                    self._create_game(instance, matchups=game_competitors, child_num=child_num)
                matchup_count += 1

        season_playoffs = season_playoffs or self.season_playoffs

        if season_playoffs:
            playoff_bids = playoff_bids or self.playoff_bids
            playoff_format = playoff_format or self.playoff_format

            self._create_tournament(instance, playoff_format, 1, playoff_bids)

        return instance

    def create_event(self, league=None, parent_event=None):
        event_type = self.cleaned_data.get("event_type")

        instance = models.GameEvent(event_type=event_type,
                                    game_type=self.cleaned_data.get("game_type"),
                                    comp_type=self.cleaned_data.get("comp_type"),
                                    parent_event=parent_event,
                                    league=league)
        instance.save()

        if event_type == 1:
            self._create_game(instance)
        elif event_type == 2:
            self._create_series()
        elif event_type == 3:
            self._create_tournament()
        elif event_type == 4:
            self._create_season()

        self.instance = instance
        return instance


class GameDetailsForm(MyBaseForm):
    game_rules = forms.CharField(widget=forms.Textarea, max_length=500, required=False)
    game_date = forms.DateTimeField(required=False)
    game_venue = forms.CharField(required=False, max_length=50)
    witness = forms.CharField(required=False, max_length=50, validators=EmailValidator("Invalid Email", code="invalid"))
