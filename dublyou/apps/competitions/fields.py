from django import forms
from ..games.models import GameType


class GameField(forms.MultiValueField):
    def __init__(self, *args, **kwargs):

        fields = (
            forms.ModelChoiceField(
                empty_label="Select a game...",
                queryset=GameType.objects.values_list("id", "game_name").order_by("game_name")
            ),
            forms.CharField(
                required=False, max_length=30
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


