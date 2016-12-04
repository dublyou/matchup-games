from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.core.validators import RegexValidator, EmailValidator
from . import models
from . import fields
import re
import math
import random
from django.db import models as db
from django.utils.translation import ugettext_lazy as _

DEFAULT_INPUT_CLASSES = "form-control"

INPUT_CRITERIA = {
        "event_type": range(1, 5),
        "event_name": r"^[-\s\.\w\d]{1,20}$",
        "custom_game": r"^[-\s\.\w\d]{1,20}$",
        "participant_type": range(1, 3),
        "num_participants": range(2, 33),
        "competitor": "email",
        "participants_per_team": range(2, 33),
        "series_games": range(3, 16, 2),
        "tourney_type": range(1, 3),
        "tourney_seeds": range(1, 3),
        "season_scheduling_type": range(1, 3),
        "round_robin": range(1, 11),
        "season_games": range(2, 163, 2),
        "playoff_bids": range(2, 33),
        "playoff_format": {1, 2, "series"},
        "playoff_series_games": range(3, 8, 2),
        "num_events": range(2, 17),
        "game_rules": r"^[-\n\s\.\w\d]{1,300}$",
        "game_location": "^[-\s\.\w\d]{1,30}$",
}


class MyBaseForm(forms.Form):

    def __init__(self, *args, **kwargs):
        super(MyBaseForm, self).__init__(*args, **kwargs)

        for field in self.fields:
            field.widget.attrs.update({
                'class': DEFAULT_INPUT_CLASSES
            })

    def as_input_group(self):
        return self._html_output(
            normal_row='<div class="input-group">%(errors)s<span class="input-group-addon hidden-xs">%(label)s</span> %(field)s%(help_text)s</div>',
            error_row='<li>%s</li>',
            row_ender='</div>',
            help_text_html=' <span class="helptext">%s</span>',
            errors_on_separate_row=False)


class MyBaseModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(MyBaseModelForm, self).__init__(*args, **kwargs)

        for field in self.fields:
            field.widget.attrs.update({
                'class': DEFAULT_INPUT_CLASSES
            })

    def as_input_group(self):
        return self._html_output(
            normal_row='<div class="input-group">%(errors)s<span class="input-group-addon hidden-xs">%(label)s</span> %(field)s%(help_text)s</div>',
            error_row='<li>%s</li>',
            row_ender='</div>',
            help_text_html=' <span class="helptext">%s</span>',
            errors_on_separate_row=False)


class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True, max_length=50)
    first_name = forms.CharField(required=True, max_length=30)
    last_name = forms.CharField(required=True, max_length=30)

    def __init__(self, *args, **kwargs):
        super(UserCreationForm, self).__init__(*args, **kwargs)

        for field in self.fields:
            field.widget.attrs.update({
                'class': DEFAULT_INPUT_CLASSES
            })

    class Meta:
        model = User
        fields = ("email", "password1", "password2", "first_name", "last_name")

    def as_input_group(self):
        return self._html_output(
            normal_row='<div class="input-group">%(errors)s<span class="input-group-addon hidden-xs">%(label)s</span> %(field)s%(help_text)s</div>',
            error_row='<li>%s</li>',
            row_ender='</div>',
            help_text_html=' <span class="helptext">%s</span>',
            errors_on_separate_row=False)

    def save(self, commit=True):
        user = super(UserCreationForm, self).save(commit=False)

        user.username = self.cleaned_data["email"]
        user.email = self.cleaned_data["email"]
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]

        if commit:
            user.save()

        return user


class CompetitorForm(MyBaseForm):
    competitor = forms.CharField(validators=EmailValidator(code="invalid"))
    user = None

    def clean(self):
        cleaned_data = super(CompetitorForm, self).clean()

        try:
            self.user = User.objects.get(username=cleaned_data["competitor"])
        except User.DoesNotExist:
            return "Create Temp User and Send Invitation Email"

    def save(self, parent_event):
        instance = models.EventCompetitors({"event": parent_event,
                                            "user": self.user
                                            })
        instance.save()
        return instance


class GameForm(MyBaseModelForm):

    class Meta:
        model = models.Game
        fields = ("game_type", "game_date", "game_venue", "witness_id")


class MatchupForm(MyBaseModelForm):

    class Meta:
        model = models.Matchup
        fields = ("game", "team", "game_on", "round", "place", "score", "seed")


class GameEventForm(MyBaseModelForm):

    class Meta:
        model = models.GameEvent
        fields = ("event_name", "event_type", "min_games", "num_competitors")

class CompParamForm(MyBaseForm):
    comp_type = forms.ChoiceField(label="Competitor Type", choices=models.COMP_TYPES)
    split_teams = forms.ChoiceField(choices=models.SPLIT_TEAMS, required=False)
    players_per_team = forms.IntegerField(min_value=2, max_value=32, required=False)
    league = forms.CharField(required=False, max_length=50)

    def clean(self):
        cleaned_data = super(CompParamForm, self).clean()
        if cleaned_data["comp_type"] == 2:
            if "split_teams" not in cleaned_data:
                self.add_error("league", forms.ValidationError(message="Invalid input", code="invalid"))
            if "players_per_team" not in cleaned_data:
                self.add_error("league", forms.ValidationError(message="Invalid input", code="invalid"))

        if cleaned_data["comp_type"] == 3:
            try:
                league = models.League.objects.get(league_name=cleaned_data["league"])
            except models.League.DoesNotExist:
                self.add_error("league", forms.ValidationError(message="League does not exist", code="invalid"))


class CreateGameForm(MyBaseForm):

    event_type = forms.ChoiceField(choices=models.EVENT_TYPES, required=False)
    event_name = forms.CharField(required=False, max_length=50)
    game_type = fields.GameField(required=False)
    comp_type = forms.ChoiceField(label="Competitor Type", choices=models.COMP_TYPES)
    split_teams = forms.ChoiceField(choices=models.SPLIT_TEAMS, required=False)
    players_per_team = forms.IntegerField(min_value=2, max_value=32, required=False)
    league = forms.CharField(required=False, max_length=50)
    series_games = forms.IntegerField(min_value=3, max_value=15, required=False)
    tourney_type = forms.ChoiceField(choices=models.TOURNEY_TYPES, required=False)
    tourney_seeds = forms.ChoiceField(choices=models.TOURNEY_SEEDS, required=False)
    season_games = fields.SeasonGamesField(required=False)
    season_playoffs = fields.PlayoffField()
    game_rules = forms.CharField(widget=forms.Textarea, max_length=500, required=False)
    game_date = forms.DateTimeField(required=False)
    game_venue = forms.CharField(required=False, max_length=50)
    witness = forms.CharField(required=False, max_length=50, validators=EmailValidator("Invalid Email", code="invalid"))

    def __init__(self, *args, **kwargs):
        self.save_data = {}

        if "competitors" in kwargs:
            self.competitors = kwargs.pop('competitors')

        if "user" in kwargs:
            self.user = kwargs.pop('user')

        super(CreateGameForm, self).__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super(CreateGameForm, self).clean()

        # clean event_type dependent inputs
        event_type = cleaned_data.get("event_type")

        if event_type in range(1, 5) or event_type == "":
            if event_type != "":

                dependent_inputs = {1: ["series_games"],
                                    2: ["tourney_type", "tourney_seeds"],
                                    3: ["season_games"],
                                    4: []
                                    }

                dependent_inputs = dependent_inputs[event_type]

            else:
                dependent_inputs = []

            if event_type != 4:
                dependent_inputs.append("game_type")

            for input_name in dependent_inputs:
                criteria = INPUT_CRITERIA[input_name]
                if type(criteria) is str:
                    if not re.match(criteria, cleaned_data[input_name]):
                        self.add_error(input_name, forms.ValidationError(message="Invalid input", code="invalid"))
                elif cleaned_data[input_name] not in criteria:
                    self.add_error(input_name, forms.ValidationError(message="Invalid input", code="invalid"))

        else:
            self.add_error("event_type", forms.ValidationError("Invalid Event Type", code="invalid"))

    def set_competitors(self, competitors):
        self.competitors = competitors

    def _create_game(self, parent_event=None, competitors=None, child_num=1):
        data = {"game_type": self.cleaned_data.get("game_type"),
                "parent_event": parent_event,
                "child_num": child_num,
                "creator": self.user
                }
        game = models.Game(data)
        game.save()

        data = {"game": game}

        competitors = competitors or self.competitors

        for competitor in competitors:
            data["user"] = competitor
            data["seed"] = competitor.seed
            matchup = models.Matchup(data)
            matchup.save()

        return game

    def _create_series(self, parent_event=None, series_games=None, competitors=None, child_num=1):
        series_games = series_games or self.cleaned_data.get("series_games")

        instance = models.GameEvent({"event_type": 1,
                                     "game_type": self.cleaned_data.get("game_type"),
                                     "comp_type": self.cleaned_data["comp_type"],
                                     "num_children": series_games,
                                     "parent_event": parent_event,
                                     "child_num": child_num,
                                     "creator": self.user})
        instance.save()

        for x in range(1, series_games + 1):
            self._create_game(instance, competitors, child_num=x)

        return instance

    def _create_tournament(self, parent_event, tourney_type=None, tourney_seeds=None, competitors=None, child_num=1):
        if competitors:
            num_competitors = len(competitors)
        else:
            num_competitors = len(self.competitors)
            competitors = self.competitors

        tourney_rounds = math.ceil(math.log(num_competitors, 2))
        tourney_seeds = tourney_seeds or self.cleaned_data.get("tourney_seeds")
        tourney_type = tourney_type or self.cleaned_data.get("tourney_type")

        games = ((2 ** tourney_rounds) - 1) * tourney_type
        instance = models.GameEvent({"event_type": 2,
                                     "game_type": self.cleaned_data.get("game_type"),
                                     "comp_type": self.cleaned_data.get("comp_type"),
                                     "num_children": games,
                                     "parent_event": parent_event,
                                     "child_num": child_num,
                                     "creator": self.user})
        instance.save()

        round1_slots = 2**tourney_rounds
        round1_byes = round1_slots - num_competitors
        round1_games = (round1_slots/2) - round1_byes

        if tourney_seeds == 1:
            random.shuffle(competitors)

        for x in range(0, round1_games):
            favorite_seed = int((round1_slots/2) - (round1_games - x) + 1)
            underdog_seed = (round1_slots + 1) - favorite_seed
            game_competitors = [competitors[favorite_seed], competitors[underdog_seed]]
            self._create_game(instance, game_competitors, child_num=x+1)

        return instance

    def _create_season(self, parent_event=None, season_games=None, competitors=None, child_num=1):

        season_games = season_games or self.cleaned_data.get("season_games")

        instance = models.GameEvent({"event_type": 3,
                                     "game_type": self.cleaned_data.get("game_type"),
                                     "comp_type": self.cleaned_data.get("comp_type"),
                                     "num_children": season_games,
                                     "parent_event": parent_event,
                                     "child_num": child_num,
                                     "creator": self.user})
        instance.save()

        matchup_count = 1

        if competitors:
            num_competitors = len(competitors)
        else:
            num_competitors = len(self.competitors)
            competitors = self.competitors

        for x in range(1, int(season_games/2) + 1):
            matchup_count = 1 if matchup_count == num_competitors else matchup_count

            for i in range(0, num_competitors):
                opp_i = (matchup_count + i) % num_competitors
                game_competitors = [competitors[i], competitors[opp_i]]
                child_num = ((x - 1) * num_competitors) + i + 1
                self._create_game(instance, game_competitors, child_num=child_num)

        return instance

    def save(self, parent_event=None):

        event_type = self.cleaned_data.get("event_type")

        if event_type in range(1, 5):

            if event_type == 1:
                instance = self._create_series(parent_event)
            elif event_type == 2:
                instance = self._create_tournament(parent_event)
            elif event_type == 3:
                instance = self._create_season(parent_event)
            else:
                instance = models.GameEvent({"event_type": 3,
                                             "game_type": self.cleaned_data.get("game_type"),
                                             "comp_type": self.cleaned_data.get("comp_type"),
                                             "num_children": 1,
                                             "creator": self.user})

        else:
            instance = self._create_game(parent_event)

        return instance
