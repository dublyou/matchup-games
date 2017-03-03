from django import forms

from ...forms import MyBaseModelForm, MyBaseForm
from . import models


class GameForm(MyBaseModelForm):
    class Meta:
        model = models.Game
        fields = ["name", "game_type", "description", "inventor", "game_image"]
        widgets = {"description": forms.Textarea()}

    def clean(self):
        cleaned_data = super(GameForm, self).clean()
        game_name = cleaned_data.get('name')
        if game_name:
            if models.Game.objects.filter(name=game_name).exists():
                raise forms.ValidationError(
                    'Name already exist',
                    code='duplicate'
                )

    def save(self, commit=True):
        instance = super(GameForm, self).save(commit=False)
        instance.creator = self.request.user
        if commit:
            instance.save()
        return instance
