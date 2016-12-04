from django import forms
from django.contrib.auth.models import User
from django.core.validators import RegexValidator, EmailValidator
from . import models
from ...forms import MyBaseForm
# from django.utils.translation import ugettext_lazy as _

NAME_REGEX = r"^[-\s\.\w\d]{1,30}$"


class CompetitorForm(MyBaseForm):
    competitor = forms.CharField(validators=[EmailValidator(code="invalid")])
    team = forms.ChoiceField(required=False)
    division_name = forms.CharField(max_length="30", required=False, validators=[RegexValidator(NAME_REGEX)])
    user = None

    def __init__(self, *args, **kwargs):
        self.teams = None

        if "teams" in kwargs:
            self.teams = kwargs.pop('teams')
        super(CompetitorForm, self).__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super(CompetitorForm, self).clean()

        try:
            self.user = User.objects.get(username=cleaned_data["competitor"])
        except User.DoesNotExist:
            return "Create Temp User and Send Invitation Email"

        if self.teams:
            if cleaned_data["team"] not in self.teams:
                self.add_error("team", forms.ValidationError(message="Invalid team", code="invalid"))

    def save(self, league):

        instance = models.LeagueMember.objects.create(league=league,
                                                      member=self.user,
                                                      team=self.cleaned_data["team"])
        return instance


class BaseCompetitorFormSet(forms.BaseFormSet):
    def clean(self):
        if any(self.errors):
            return

        competitors = []
        duplicates = False

        for form in self.forms:
            if form.cleaned_data:
                competitor = form.cleaned_data['competitor']

                if competitor:
                    if competitor in competitors:
                        duplicates = True
                    competitors.append(competitor)

                if duplicates:
                    raise forms.ValidationError(
                        'Duplicate competitor.',
                        code='duplicate'
                    )


class TeamForm(MyBaseForm):
    team_name = forms.CharField(max_length="30", validators=[RegexValidator(NAME_REGEX)])
    division_name = forms.CharField(max_length="30", required=False, validators=[RegexValidator(NAME_REGEX)])

    def save(self, league, captain):
        instance = models.Team.create(league=league,
                                      team_name=self.cleaned_data.get("team_name"),
                                      captain=captain,
                                      division=self.cleaned_data["division_name"]
                                      )
        return instance


class BaseTeamFormSet(forms.BaseFormSet):
    def clean(self):
        if any(self.errors):
            return

        teams = []
        duplicates = False

        for form in self.forms:
            if form.cleaned_data:
                team_name = form.cleaned_data['team_name']

                if team_name:
                    if team_name in teams:
                        duplicates = True
                    teams.append(team_name)

                if duplicates:
                    raise forms.ValidationError(
                        'Duplicate team names.',
                        code='duplicate'
                    )
