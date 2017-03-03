import hashlib
import random

from django import forms
from django.contrib.auth.models import User
from django.core.validators import RegexValidator, EmailValidator

from invitations.models import Invitation
from . import models
from ...forms import MyBaseForm, MyBaseModelForm
# from django.utils.translation import ugettext_lazy as _


class LeagueForm(MyBaseModelForm):
    def __init__(self, *args, **kwargs):
        instance = kwargs.get("instance", None)
        super(LeagueForm, self).__init__(*args, **kwargs)
        if instance:
            self.fields.pop("matchup_type")

    class Meta:
        model = models.League
        fields = ['name', 'abbrev', 'matchup_type', 'games', 'max_members']

    def save(self, commit=True):
        league = super(LeagueForm, self).save(commit=False)
        if league.pk is None:
            league.commissioner = self.user.profile

        if commit:
            league.save()
            self.save_m2m()
        return league


class AddTeamPlayerForm(MyBaseModelForm):
    competitor = forms.CharField(validators=[EmailValidator(code="invalid")], required=False, max_length=50)
    invite = None

    class Meta:
        model = models.LeagueInvite
        fields = ['player']

    def __init__(self, *args, **kwargs):
        self.team = kwargs.pop("parent", None)
        super(AddTeamPlayerForm, self).__init__(*args, **kwargs)
        self.fields["player"].required = False

    def clean(self):
        cleaned_data = super(AddTeamPlayerForm, self).clean()
        if cleaned_data["player"]:
            player = models.LeaguePlayer.objects.filter(player=cleaned_data['player'])
            if player.exists():
                raise forms.ValidationError(
                    'Player already exists.',
                    code='duplicate'
                )
        else:
            competitor = cleaned_data["competitor"]
            if competitor:
                user = User.objects.filter(email=competitor)

                if user.exists():
                    cleaned_data["player"] = user.profile
                else:
                    self.invite = Invitation.create(email=competitor, inviter=self.request.user)
                    self.invite.send_invitation(self.request)
        return cleaned_data

    def save(self, commit=True):
        cleaned_data = self.cleaned_data
        if cleaned_data['user']:
            old_pending_players = models.LeagueInvite.objects.filter(player=cleaned_data['player'],
                                                                     league=self.league,
                                                                     team=self.team,
                                                                     invite_type=2)
            if old_pending_players.exists():
                old_pending_players.delete()
        pending_player = super(AddPlayerForm).save(commit=False)
        pending_player.league = self.league
        pending_player.invite = self.invite
        pending_player.invite_type = 2

        if commit:
            pending_player.save()
        return pending_player


class AddPlayerForm(MyBaseModelForm):
    player_search = forms.CharField(validators=[EmailValidator(code="invalid")], required=False, max_length=50)
    invite = None

    class Meta:
        model = models.LeagueInvite
        fields = ['team', 'player', 'division']
        widgets = {'player': forms.HiddenInput}

    def __init__(self, *args, **kwargs):
        self.league = kwargs.pop("parent", None)
        super(AddPlayerForm, self).__init__(*args, **kwargs)
        self.fields["player"].required = False
        player_search = self.fields["player_search"]
        player_search.widget.attrs.update({
            "data-content": "Search for an existing user or invite a new user by entering their email below.",
            "data-placement": "top",
            "data-container": "body",
            "data-trigger": "focus"
        })
        if self.league.matchup_type == 2:
            self.fields.pop('division')
            self.fields['team'].queryset = \
                self.league.team_set.order_by("team_name")
        else:
            self.fields.pop('team')
            self.fields['division'].queryset = \
                self.league.divisions.order_by("division_name")

    def clean(self):
        cleaned_data = super(AddPlayerForm, self).clean()
        if cleaned_data["player"]:
            player = models.LeaguePlayer.objects.filter(player=cleaned_data['player'])
            if player.exists():
                raise forms.ValidationError(
                    'Player already exists.',
                    code='duplicate'
                )
        else:
            player_email = cleaned_data["player_search"]
            if player_email:
                user = User.objects.filter(email=player_email)

                if user.exists():
                    cleaned_data["player"] = user.profile
                else:
                    self.invite = Invitation.create(email=player_email, inviter=self.request.user)
                    self.invite.send_invitation(self.request)
        return cleaned_data

    def save(self, commit=True):
        cleaned_data = self.cleaned_data
        if cleaned_data['player']:
            old_pending_players = models.LeagueInvite.objects.filter(player=cleaned_data['player'],
                                                                     league=self.league,
                                                                     invite_type=1)
            if old_pending_players.exists():
                old_pending_players.delete()
        pending_player = super(AddPlayerForm).save(commit=False)
        pending_player.league = self.league
        pending_player.invite = self.invite
        pending_player.approved = True

        if commit:
            pending_player.save()
        return pending_player


class EditPlayerForm(MyBaseModelForm):
    def __init__(self, *args, **kwargs):
        league = kwargs.pop("parent", None)
        super(EditPlayerForm, self).__init__(*args, **kwargs)
        if league:
            if league.matchup_type == 2:
                self.fields.pop("division")
            else:
                self.fields.pop("team")

    class Meta:
        model = models.LeaguePlayer
        fields = ['team', 'division', 'admin', 'status']


class EditTeamPlayerForm(MyBaseModelForm):

    class Meta:
        model = models.LeaguePlayer
        fields = ['status']


class TeamForm(MyBaseModelForm):
    division_name = forms.CharField(max_length=30, required=False)

    class Meta:
        model = models.Team
        fields = ['name', 'abbrev', 'division', 'captain']

    def __init__(self, *args, **kwargs):
        self.league = kwargs.pop("parent", None)
        super(TeamForm, self).__init__(*args, **kwargs)
        div_field = self.fields['division']
        div_field.queryset = \
            self.league.divisions.order_by("division_name")
        div_field_classes = div_field.widget.attrs.get("class", "")
        div_field.widget.attrs.update({
            "class": div_field_classes + " hidden-select combobox",
            "data-combobox-container": "#division_combobox"
        })
        self.fields['division_name'].widget.attrs.update({
            "autocomplete": "off"
        })
        if self.instance is None:
            self.fields["captain"].queryset = self.instance.players.all()
            if self.request.user.profile != self.league.commissioner:
                self.fields.pop("division")
                self.fields.pop("division_name")
        else:
            self.fields.pop('captain')

    def clean(self):
        cleaned_data = super(TeamForm, self).clean()
        team = self.league.teams.filter(team_name=cleaned_data['team_name'])
        if team.exists():
            raise forms.ValidationError(
                'Team name already exists.',
                code='duplicate'
            )
        return cleaned_data

    def save(self, commit=True):
        cleaned_data = self.cleaned_data
        if not cleaned_data["division"] and cleaned_data["division_name"]:
            self.cleaned_data["division"] = models.LeagueDivision.create(league=self.league,
                                                                         division_name=cleaned_data["division_name"])
        team = super(TeamForm).save(commit=False)
        if team.pk is None:
            team.league = self.league
        if commit:
            team.save()
        return team


class LeagueSignUpForm(MyBaseModelForm):
    change_key = forms.BooleanField()

    class Meta:
        model = models.LeagueSignUpPage
        fields = ['expiration', 'msg_image']

    def __init__(self, *args, **kwargs):
        self.league = kwargs.pop("instance", None)
        if getattr(self.league, "signup_page", None):
            kwargs["instance"] = self.league.signup_page
        super(LeagueSignUpForm, self).__init__(*args, **kwargs)
        if not self.instance.pk:
            self.fields.pop("change_key")

    def save(self, commit=True):
        instance = super(LeagueSignUpForm, self).save(commit=False)
        if not instance.pk:
            instance.league = self.league
        if not instance.pk or self.cleaned_data.get("change_key"):
            salt = hashlib.sha1(str(random.random()).encode()).hexdigest()[:5]
            instance.verification_key = hashlib.sha1((salt + self.league.name).encode()).hexdigest()
        if commit:
            instance.save()
        return instance.league
