from django import forms
from ...forms import MyBaseModelForm
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


class CreateMatchups(object):

    def __init__(self, competition, league):
        event_type = competition.event_type
        self.competition = competition
        self.competitors = league.league_members.all() if league.matchup_type == 1 else league.team_set.all()

        if event_type == 1:
            self._create_matchup()
        elif event_type == 2:
            self._create_series()
        elif event_type == 3:
            self._create_tournament()
        elif event_type == 4:
            self._create_season()
        elif event_type == 5:
            for child in competition.competition_set.all():
                event_type = child.event_type
                self.competition = child
                if event_type == 1:
                    self._create_matchup()
                elif event_type == 2:
                    self._create_series()
                elif event_type == 3:
                    self._create_tournament()
                elif event_type == 4:
                    self._create_season()

    def _create_matchup(self, parent_id=None, parent_type=None, child_num=1, matchups=None,
                        tourney_round=None, status=1):

        instance = models.Matchup(competition=self.competition,
                                  status=status,
                                  tourney_round=tourney_round,
                                  child_num=child_num
                                  )

        if parent_id:
            instance.parent_id = parent_id
            instance.parent_type = parent_type

        instance.save()

        matchups = matchups or self.competitors

        mc = models.MatchupCompetitor(matchup=instance)

        for i, matchup in enumerate(matchups):
            if "id" in matchup:
                if "type" in matchup:
                    if "outcome" in matchup:
                        mc.dependent_outcome = matchup["outcome"]
                    mc.dependent_type = matchup["type"]
                    mc.dependent_id = matchup["id"]

                else:
                    if self.competition.matchup_type == 1:
                        mc.player = matchup["id"]
                    else:
                        mc.team = matchup["id"]

                if "seed" in matchup:
                    mc.seed = matchup["seed"]

            else:
                mc.seed = i
                if self.competition.matchup_type == 1:
                    mc.player = matchup
                else:
                    mc.team = matchup

            mc.save()

        return instance

    def _create_series(self, parent_event=None, series_type=None, series_games=None,
                       competitors=None, child_num=1, tourney_round=None, status=1):
        series_type = series_type or self.competition.series_type
        series_games = series_games or self.competition.series_games

        if parent_event:
            instance = models.Series.create(series_type=series_type,
                                            series_games=series_games,
                                            competition=self.competition,
                                            status=status,
                                            tourney_round=tourney_round,
                                            child_num=child_num
                                            )
        else:
            instance = self.competition.series_set.all()[0]

        competitors = competitors or self.competitors

        for x in range(1, series_games + 1):
            if series_type == 1 and x >= int(series_games/2) + 1:
                status = 5
            self._create_matchup(parent_id=instance.id, parent_type=2, child_num=x,
                                 matchups=competitors, status=status)

        return instance

    def _create_round(self, tournament, current_ids, round_slots, round_num=1,
                      round_type=None, series_games=None, status=1):

        tourney_round = models.TourneyRound.create(tournament=tournament,
                                                   round_type=round_type,
                                                   round_num=round_num,
                                                   )
        ids = []
        round_games = int(round_slots/2) - (round_slots - len(current_ids))

        for y in range(0, round_games):
            favorite_seed = int((round_slots / 2) - (round_games - y) + 1)
            underdog_seed = (round_slots + 1) - favorite_seed
            if "type" in current_ids[favorite_seed]:
                current_ids[favorite_seed]["outcome"] = 1
            if "type" in current_ids[underdog_seed]:
                current_ids[underdog_seed]["outcome"] = 1
            if round_type == 2:
                if round_num % 2 == 0:
                    current_ids[favorite_seed]["outcome"] = 2
                if round_num == 1:
                    current_ids[favorite_seed]["outcome"] = 2
                    current_ids[underdog_seed]["outcome"] = 2
            if status == 5 and round_type == 1:
                current_ids[favorite_seed]["outcome"] = 2

            matchups = [current_ids[favorite_seed], current_ids[underdog_seed]]
            mc = {}

            if series_games:
                new_id = self._create_series(parent_event=tournament, child_num=y + 1, competitors=matchups,
                                             series_games=series_games, series_type=1, tourney_round=tourney_round,
                                             status=status)
                mc["type"] = 2
            else:
                new_id = self._create_matchup(parent_type=3, parent_id=tournament.id, child_num=y + 1,
                                              matchups=matchups, tourney_round=tourney_round, status=status)
                mc["type"] = 1
            mc["id"] = new_id.id
            ids = [mc] + ids
        return ids

    def _create_tournament(self, parent_event=None, tourney_type=None,
                           tourney_seeds=None, competitors=None, playoff=False):
        if competitors:
            num_competitors = len(competitors)
        else:
            num_competitors = len(self.competitors)
            competitors = self.competitors

        tourney_seeds = tourney_seeds or self.competition.tourney_seeds
        tourney_type = tourney_type or self.competition.tourney_type

        if parent_event:
            instance = models.Tournament.create(tourney_type=tourney_type,
                                                tourney_seeds=tourney_seeds,
                                                competition=self.competition,
                                                status=1
                                                )
        else:
            instance = self.competition.tournament_set.all()[0]

        if tourney_seeds == 1:
            random.shuffle(competitors)

        tourney_rounds = math.ceil(math.log(num_competitors, 2))
        round1_byes = (2 ** tourney_rounds) - num_competitors

        bye_ids = []
        ids = []
        l_ids = []
        for i, competitor in enumerate(competitors):
            mc = {"id": competitor, "seed": i}
            if playoff:
                mc["type"] = 4
            ids.append(mc)
            if i < round1_byes:
                bye_ids.append(mc)

        for x in range(0, tourney_rounds):

            round_slots = 2 ** (tourney_rounds - x)

            ids = self._create_round(tournament=instance, current_ids=ids, round_slots=round_slots,
                                     round_num=x+1, round_type=1)
            if tourney_type == 2:
                if x == 0:

                    round1_byes = int(round_slots/2) - len(ids)
                    l_bye_ids = []
                    for i, l_id in enumerate(ids):
                        if i < round1_byes:
                            l_bye_ids.append(l_id)
                        else:
                            l_ids.append(l_id)

                    round_slots = int(round_slots/2)

                    l_ids = self._create_round(tournament=instance, current_ids=l_ids,
                                               round_slots=round_slots, round_num=1, round_type=2)

                    l_ids = l_bye_ids + l_ids
                else:
                    round_num = x * 2
                    l_ids = ids + l_ids
                    l_ids = self._create_round(tournament=instance, current_ids=l_ids,
                                               round_slots=round_slots, round_num=round_num, round_type=2)
                    l_ids = self._create_round(tournament=instance, current_ids=l_ids,
                                               round_slots=round_slots, round_num=round_num + 1, round_type=2)

            if x == 0:
                ids = bye_ids + ids

        if tourney_type == 2:
            ids = self._create_round(tournament=instance, current_ids=ids + l_ids, round_slots=2,
                                     round_num=tourney_rounds + 1, round_type=1)
            self._create_round(tournament=instance, current_ids=ids * 2, round_slots=2,
                               round_num=tourney_rounds + 2, round_type=1, status=5)

        return instance

    def _create_season(self, parent_event=None, season_type=None, season_games=None, competitors=None,
                       season_playoffs=None, playoff_bids=None, playoff_format=None):
        season_type = season_type or self.competition.season_type
        season_games = season_games or self.competition.season_games

        if competitors:
            num_competitors = len(competitors)
        else:
            num_competitors = len(self.competitors)
            competitors = self.competitors

        games = season_games * num_competitors if season_type == 1 else season_games

        if parent_event:
            instance = models.Season.create(season_type=season_type,
                                            season_games=season_games,
                                            season_playoffs=season_playoffs,
                                            playoff_bids=playoff_bids,
                                            playoff_format=playoff_format,
                                            competition=self.competition,
                                            status=1
                                            )
        else:
            instance = self.competition.season_set.all()[0]

        matchup_count = 1

        if season_type == 1:
            for r in range(0, games):
                for i in range(0, num_competitors):
                    for x in range(i + 1, num_competitors):
                        game_competitors = [competitors[i], competitors[x]]
                        child_num = (r * i) + (i * (x - i + 2)) + x - i + 2
                        self._create_matchup(parent_type=4, parent_id=instance.id, matchups=game_competitors,
                                             child_num=child_num)
        else:
            for x in range(1, int(games / 2) + 1):
                matchup_count = 1 if matchup_count == num_competitors else matchup_count

                for i in range(0, num_competitors):
                    opp_i = (matchup_count + i) % num_competitors
                    game_competitors = [competitors[i], competitors[opp_i]]
                    child_num = ((x - 1) * num_competitors) + i + 1
                    self._create_matchup(parent_type=4, parent_id=instance.id, matchups=game_competitors,
                                         child_num=child_num)
                matchup_count += 1

        season_playoffs = season_playoffs or self.competition.season_playoffs

        if season_playoffs:
            playoff_bids = playoff_bids or self.competition.playoff_bids
            playoff_format = playoff_format or self.competition.playoff_format

            self._create_tournament(parent_event=instance, tourney_type=playoff_format, tourney_seeds=2,
                                    competitors=[instance.id]*playoff_bids, playoff=True)

        return instance


class CompetitorInfoForm(MyBaseModelForm):
    dependent_inputs = [{"name": "signup_method",
                         "fields": {
                             1: [{"name": "matchup_type",
                                  "fields": {
                                      1: [],
                                      2: ["split_teams", "players_per_team"]
                                  }}
                                 ],
                             2: ["league"]
                         }}
                        ]

    class Meta:
        model = models.CompetitorInfo
        fields = '__all__'
        exclude = ['competition']

    def __init__(self, user, *args, **kwargs):
        super(CompetitorInfoForm, self).__init__(*args, **kwargs)
        self.fields['league'].queryset = \
            user.comissioner_set.values_list("id", "league_name").order_by("league_name")


class CompetitionForm(MyBaseModelForm):
    game_type = fields.GameField(required=False)

    dependent_inputs = [{"name": "event_type",
                         "fields": {
                             1: ["game_type"],
                             2: ["game_type"],
                             3: ["game_type"],
                             4: ["game_type"],
                             5: []
                         }}
                        ]

    class Meta:
        model = models.Competition
        fields = '__all__'
        exclude = ['parent', 'status', 'creation_datetime']

    def __init__(self, parent=None, *args, **kwargs):
        super(CompetitionForm, self).__init__(*args, **kwargs)
        if parent:
            self.fields['event_type'].choices = self.fields['event_type'].choices[0:4]

    def clean(self):
        super(CompetitionForm, self).clean()

        # clean event_type dependent inputs
        for input_tree in self.dependent_inputs:
            self.clean_dependent_inputs(input_tree, INPUT_CRITERIA)

    def save(self, commit=True, parent=None):
        competition = super(CompetitionForm).save(commit=False)

        if parent:
            competition.parent = parent

        if commit:
            competition.save()
        return competition


class EventTypeForm(MyBaseModelForm):
    def save(self, commit=True, competition=None):
        event = super(CompetitionForm).save(commit=False)

        if competition:
            event.competition = competition
        else:
            commit = False

        if commit:
            event.save()
        return event


class SeriesForm(EventTypeForm):
    series_games = forms.ChoiceField(choices=[(x, x) for x in INPUT_CRITERIA["series_games"]])

    class Meta:
        model = models.Series
        fields = ['series_type', 'series_games']


class TournamentForm(EventTypeForm):
    class Meta:
        model = models.Tournament
        fields = ['tourney_type', 'tourney_seeds']


class SeasonForm(EventTypeForm):
    season_games = forms.ChoiceField(choices=[(x, x) for x in INPUT_CRITERIA["season_games"]])
    playoff_bids = forms.ChoiceField(choices=[(x, x) for x in INPUT_CRITERIA["playoff_bids"]], required=False)

    dependent_inputs = [{"name": "season_playoffs",
                         "fields": {
                             True: ["playoff_bids", "playoff_format"],
                             False: []
                         }}
                        ]

    class Meta:
        model = models.Season
        fields = '__all__'
        exclude = ['competition', 'status']
