from django import forms
from . import models
from django.db import models as db
from django.core.validators import RegexValidator, EmailValidator


class GameField(forms.MultiValueField):
    def __init__(self, *args, **kwargs):

        fields = (
            forms.ModelChoiceField(
                empty_label="Select a game...",
                queryset=db.GameType.objects.values_list("id", "game_name").order_by("game_name")
            ),
            forms.CharField(
                required=False, max_length=25
            ),
        )
        super(GameField, self).__init__(
            fields=fields,
            require_all_fields=False, *args, **kwargs
        )

    def compress(self, data_list):
        if data_list[0] == "custom_game":
            return data_list[1]
        else:
            return data_list[0]


class SeasonGamesField(forms.MultiValueField):
    def __init__(self, *args, **kwargs):

        fields = (
            forms.ChoiceField(
                choices=models.SEASON_METHODS,
                required=False
            ),
            forms.IntegerField(
                min_value=2, max_value=162, required=False
            ),
            forms.IntegerField(
                min_value=2, max_value=32, required=False
            )
        )
        super(SeasonGamesField, self).__init__(
            fields=fields,
            require_all_fields=False, *args, **kwargs
        )

    def compress(self, data_list):
        if data_list[0] == 1:
            return "round robin:" + str(data_list[2])
        else:
            return data_list[1]


class UserField(forms.MultiValueField):
    def __init__(self, *args, **kwargs):

        fields = (
            forms.CharField(
                required=False,
                validators=EmailValidator()
            ),
            forms.IntegerField(
                min_value=2, max_value=162, required=False
            )
        )
        super(UserField, self).__init__(
            fields=fields,
            require_all_fields=False, *args, **kwargs
        )

    def compress(self, data_list):
        if data_list[0] == 1:
            return "round robin:" + str(data_list[2])
        else:
            return data_list[1]


class PlayoffField(forms.MultiValueField):
    def __init__(self, *args, **kwargs):

        fields = (
            forms.BooleanField(
                required=False,
                validators=EmailValidator()
            ),
            forms.IntegerField(
                label="Playoff Bids",
                min_value=2, max_value=32, required=False
            ),
            forms.ChoiceField(
                label="Playoff Format",
                choices=models.PLAYOFF_FORMATS, required=False
            ),
            forms.IntegerField(
                label="Playoff Series Games",
                min_value=3, max_value=15, required=False
            )
        )
        super(PlayoffField, self).__init__(
            fields=fields,
            require_all_fields=False, *args, **kwargs
        )

    def compress(self, data_list):
        if data_list[0]:
            return data_list[1:]
        else:
            return ""


