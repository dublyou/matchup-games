from django import forms
from django.contrib.auth.models import User
from django.core.validators import RegexValidator, EmailValidator
from . import models
from ..competitions.fields import GameField
from ...forms import MyBaseForm, MyBaseModelForm
# from django.utils.translation import ugettext_lazy as _

NAME_REGEX = r"^[-\s\.\w\d]{1,30}$"


class CompetitorForm(MyBaseForm):
    league_id = forms.IntegerField(widget=forms.HiddenInput())
    competitor = forms.CharField(validators=[EmailValidator(code="invalid")])
    division_name = forms.CharField(max_length="30", required=False, validators=[RegexValidator(NAME_REGEX)])
    user = None
    league = None
    member = None
    teams = None

    class Meta:
        model = models.LeagueMember
        fields = ['team']

    def __init__(self, user=None, league_id=None, teams=False, *args, **kwargs):
        self.user = user
        self.teams = teams

        super(CompetitorForm, self).__init__(*args, **kwargs)
        if league_id:
            try:
                self.league = models.League.objects.get(id=league_id, commissioner=self.user)
            except models.League.DoesNotExist:
                raise forms.ValidationError(message="Invalid league", code="invalid")

        if teams:
            self.fields.pop('division')
            self.fields['team'].queryset = \
                self.league.team_set.values_list("id", "team_name").order_by("team_name")
        else:
            self.fields.pop('team')

    def clean(self):
        cleaned_data = super(CompetitorForm, self).clean()

        try:
            self.league = models.League.objects.get(id=cleaned_data["league_id"], commissioner=self.user)
        except models.League.DoesNotExist:
            raise forms.ValidationError(message="Invalid league", code="invalid")

        try:
            self.member = User.objects.get(username=cleaned_data["competitor"])
        except User.DoesNotExist:
            return "Create Temp User and Send Invitation Email"

        if self.teams:
            if cleaned_data["team"] not in self.teams:
                self.add_error("team", forms.ValidationError(message="Invalid team", code="invalid"))

    def save(self, commit=True):
        league_member = super(CompetitorForm).save(commit=False)
        league_member.league = self.league
        league_member.member = self.member
        if self.teams:
            league_member.team = self.team
        else:
            if self.cleaned_data["division_name"]:
                division = models.LeagueDivision.objects.get(league=self.league,
                                                             division_name=self.cleaned_data["division_name"])
                if not division:
                    division = models.LeagueDivision.create(league=self.league,
                                                            division_name=self.cleaned_data["division_name"])
                league_member.division = division

        if commit:
            league_member.save()
        return league_member


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


class TeamForm(MyBaseModelForm):
    league_id = forms.IntegerField(widget=forms.HiddenInput())
    team_name = forms.CharField(max_length="30", validators=[RegexValidator(NAME_REGEX)])
    division_name = forms.CharField(max_length="30", required=False, validators=[RegexValidator(NAME_REGEX)])
    league = None

    class Meta:
        model = models.Team
        fields = ['team_name', 'team_abbrev']

    def __init__(self, user=None, league=None, *args, **kwargs):
        self.user = user
        super(TeamForm, self).__init__(*args, **kwargs)
        if league:
            self.fields["league_id"].initial = league.id

    def clean(self):
        cleaned_data = super(TeamForm, self).clean()

        try:
            self.league = models.League.objects.get(id=cleaned_data["league_id"], commissioner=self.user)
        except models.League.DoesNotExist:
            raise forms.ValidationError(message="Invalid league", code="invalid")

    def save(self, commit=True):
        team = super(TeamForm).save(commit=False)
        team.league = self.league
        team.captain = self.user

        if self.cleaned_data["division_name"]:
            division = models.LeagueDivision.objects.get(league=team.league,
                                                         division_name=self.cleaned_data["division_name"])
            if not division:
                division = models.LeagueDivision.create(league=team.league,
                                                        division_name=self.cleaned_data["division_name"])
            team.division = division

        if commit:
            team.save()
        return team


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


class LeagueForm(MyBaseModelForm):
    game_type = GameField(required=False)

    class Meta:
        model = models.League
        fields = ['league_name', 'league_abbrev', 'matchup_type', 'game_type', 'max_members']

    def save(self, commit=True, user=None):
        league = super(LeagueForm).save(commit=False)
        league.commissioner = user

        if commit:
            league.save()
        return league
