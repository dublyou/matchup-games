import hashlib
import random

from django import forms
from django.contrib.auth.models import User
from django.core.validators import EmailValidator, RegexValidator

from invitations.models import Invitation

from ...forms import MyBaseModelForm, MyBaseForm
from . import models
from ..leagues.models import League
from ...constants import (INPUT_CRITERIA, COMPETITION_DI,
                          MATCHUP_TYPE_DI, NAME_REGEX)
from ...fields import MultiTimeField
from ...utils import send_notification


class CompetitionSubForm(MyBaseModelForm):
    def __init__(self, *args, **kwargs):
        required = kwargs.pop("required", None)
        self.request = kwargs.pop("request", None)
        self.user = self.request.user if self.request else None
        super(CompetitionSubForm, self).__init__(*args, **kwargs)
        if required is not None:
            for name, field in self.fields.items():
                field.required = required

    def save(self, commit=True, competition=None):
        instance = super(CompetitionSubForm, self).save(commit=False)

        if not getattr(instance, "competition", False):
            if competition:
                instance.competition = competition
            else:
                commit = False

        if commit:
            instance.save()
        return instance


class SeriesForm(CompetitionSubForm):
    class Meta:
        model = models.Series
        fields = ['series_type', 'series_games']


class TournamentForm(CompetitionSubForm):
    class Meta:
        model = models.Tournament
        fields = ['tourney_type', 'tourney_seeds']


class SeasonForm(CompetitionSubForm):
    class Meta:
        model = models.Season
        fields = '__all__'
        exclude = ['competition', 'status']


class CompetitionForm(MyBaseModelForm):
    dependent_inputs = None
    form_classes = [SeriesForm, TournamentForm, SeasonForm]
    parent = None
    league = None

    time = MultiTimeField()
    competing = forms.BooleanField(label="Are you competing?", required=True, initial=True)

    class Meta:
        model = models.Competition
        fields = ['name', 'competition_type', 'game', 'matchup_type', 'split_teams', 'players_per_team',
                  'date', 'time', 'notes']
        widgets = {"notes": forms.Textarea()}

    def __init__(self, *args, **kwargs):
        self.parent = kwargs.pop("parent", None)
        initial = kwargs.get("initial")
        if initial and "league" in initial:
            league = League.object.filter(pk=initial["league"])
            if league.exists():
                self.league = league.get()
            else:
                initial.pop("league")
        super(CompetitionForm, self).__init__(*args, **kwargs)

        if self.parent:
            self.fields['competition_type'].choices = self.fields['competition_type'].choices[0:5]
            self.fields.pop("league", None)
            self.fields.pop("competing", None)
            self.fields.pop("matchup_type", None)
        if self.league:
            self.fields.pop("league", None)
        elif not self.parent and "league" in self.fields:
            self.fields['league'].queryset = \
                self.user.profile.comm_leagues.order_by("league_name")
        field_order = ['name', 'competition_type', 'game',]
        for form_class in self.form_classes:
            subform_fields = form_class(required=False, *args, **kwargs).fields
            self.fields.update(subform_fields)
            field_order += list(subform_fields.keys())
        field_order.append('matchup_type')
        self.dependent_inputs = [COMPETITION_DI, MATCHUP_TYPE_DI]
        for input_tree in self.dependent_inputs:
            self.add_actions(input_tree)
        self.order_fields(field_order)

    def clean(self):
        super(CompetitionForm, self).clean()

        for input_tree in self.dependent_inputs:
            self.clean_dependent_inputs(input_tree, INPUT_CRITERIA)

    def save(self, commit=True):
        competition = super(CompetitionForm, self).save(commit=False)
        profile = self.user.profile
        competition.parent = self.parent
        competition.creator = profile

        if commit:
            cleaned_data = self.cleaned_data
            if not self.parent:
                if self.league:
                    competition.league = self.league
                competition.save()
                if competition.league:
                    competition.invite_league()
                if cleaned_data["competing"]:
                    competition.add_competitor(player=profile)
            else:
                competition.matchup_type = self.parent.matchup_type
                competition.save()
            competition_type = cleaned_data["competition_type"]
            if competition_type in range(2, 5):
                self.form_classes[competition_type - 2](cleaned_data).save(competition=competition)
        return competition


class EditCompetitionForm(MyBaseModelForm):
    sub_form_classes = [SeriesForm, TournamentForm, SeasonForm]
    sub_instance = None
    sub_form_class = None

    time = MultiTimeField()

    class Meta:
        model = models.Competition
        fields = ["name", "game",
                  "date", "time",
                  "venue", "notes"]
        widgets = {"notes": forms.Textarea()}

    def __init__(self, *args, **kwargs):
        super(EditCompetitionForm, self).__init__(*args, **kwargs)
        if self.instance:
            comp_type = self.instance.competition_type
            if comp_type in range(2, 5):
                self.sub_instance = self.instance.competition_details
                self.sub_form_class = self.sub_form_classes[comp_type - 2]
                sub_form = self.sub_form_class(instance=self.sub_instance)
                self.fields.update(sub_form.fields)
                self.initial.update(sub_form.initial)
        self.dependent_inputs = [COMPETITION_DI]
        for input_tree in self.dependent_inputs:
            self.add_actions(input_tree)

    def save(self, commit=True):
        competition = super(EditCompetitionForm, self).save()
        if self.sub_form_class:
            self.sub_form_class(self.cleaned_data, instance=self.sub_instance).save()
        return competition


class MatchupForm(MyBaseModelForm):
    time = MultiTimeField()

    class Meta:
        model = models.Matchup
        fields = ["date", "time", "notes"]
        widgets = {"notes": forms.Textarea()}


class MatchupResultFormset(forms.BaseInlineFormSet):
    def clean(self):
        if any(self.errors):
            return
        first_place_count = 0
        form_count = self.total_form_count()
        for form in self.forms:
            place = form.cleaned_data['place']
            if place > form_count:
                form.add_error("place", "Invalid place.")
            if place == 1:
                first_place_count += 1
                if first_place_count > 1:
                    raise forms.ValidationError("Can not have multiple first places.")


class MatchupResultForm(MyBaseModelForm):
    place = forms.ChoiceField(choices=((1, 1), (2, 2)))

    class Meta:
        model = models.MatchupCompetitor
        fields = ["place"]

    def __init__(self, *args, **kwargs):
        super(MatchupResultForm, self).__init__(*args, **kwargs)
        if self.instance:
            count = self.instance.opponents.count()
            if count > 1:
                self.fields["place"].choices = ((x, x) for x in range(1, count + 2))

    def clean(self):
        cleaned_data = super(MatchupResultForm, self).clean()
        place = cleaned_data.get("place")
        if place:
            cleaned_data["place"] = int(place)
        return cleaned_data

    def save(self, commit=True):
        instance = super(MatchupResultForm, self).save(commit=True)
        print(instance.place)
        instance.update_status()
        return instance


class CompetitionSignUpForm(MyBaseModelForm):
    change_key = forms.BooleanField()

    class Meta:
        model = models.CompetitionSignUpPage
        fields = ['expiration', 'msg_image']

    def __init__(self, *args, **kwargs):
        self.competition = kwargs.pop("instance", None)
        if getattr(self.competition, "signup_page", None):
            kwargs["instance"] = self.competition.signup_page
        super(CompetitionSignUpForm, self).__init__(*args, **kwargs)
        if not self.instance.pk:
            self.fields.pop("change_key")

    def save(self, commit=True):
        instance = super(CompetitionSignUpForm, self).save(commit=False)
        if not instance.pk:
            instance.competition = self.competition
        if not instance.pk or self.cleaned_data.get("change_key"):
            salt = hashlib.sha1(str(random.random()).encode()).hexdigest()[:5]
            instance.verification_key = hashlib.sha1((salt + self.competition.name).encode()).hexdigest()
        if commit:
            instance.save()
        return instance.competition


class AddCompetitorForm(MyBaseModelForm):
    player_search = forms.CharField(validators=[EmailValidator(code="invalid")],
                                    required=False, max_length=50)
    team_name = forms.CharField(validators=[RegexValidator(NAME_REGEX)],
                                max_length=30, required=False)
    invite = None
    approved = True

    class Meta:
        model = models.CompetitionInvite
        fields = ['competitor', 'player']
        widgets = {'player': forms.HiddenInput}

    def __init__(self, *args, **kwargs):
        self.parent = kwargs.pop("parent", None)
        self.competition = self.parent if self.approved else self.parent.competition

        super(AddCompetitorForm, self).__init__(*args, **kwargs)
        self.fields["player"].required = False
        player_search = self.fields["player_search"]
        player_search.widget.attrs.update({
            "data-content": "Search for an existing user or invite a new user by entering their email below.",
            "data-placement": "top",
            "data-container": "body",
            "data-trigger": "focus"
        })
        if self.approved and self.competition.matchup_type == 2 \
                and self.competition.split_teams == 1:
            competitor_field = self.fields['competitor']
            competitor_field.queryset = \
                self.competition.competitor_set.filter(status=1).order_by("team_name")
            competitor_field_classes = competitor_field.widget.attrs.get("class", "")
            competitor_field.widget.attrs.update({
                "class": competitor_field_classes + " hidden-select combobox",
                "data-combobox-container": "#team_combobox"
            })
            self.fields['team_name'].widget.attrs.update({
                "autocomplete": "off"
            })
        else:
            self.fields.pop('competitor')
            self.fields.pop('team_name')
        self.added = False

    def clean(self):
        cleaned_data = super(AddCompetitorForm, self).clean()
        if not cleaned_data["player"]:
            player_email = cleaned_data.get("player_search", None)
            if player_email:
                user = User.objects.filter(email=player_email)

                if user.exists():
                    cleaned_data["player"] = user.get().profile
                else:
                    self.invite = Invitation.create(email=player_email, inviter=self.request.user)
            else:
                raise forms.ValidationError(
                    'must enter a valid competitor'
                )

        if self.approved and not cleaned_data.get("competitor", False) and cleaned_data.get("team_name", None):
            competitor, created = models.Competitor.objects.get_or_create(team_name=cleaned_data["team_name"],
                                                                          competition=self.competition,
                                                                          competitor_type=2)
            if created:
                competitor.status = 0
                competitor.save()
            cleaned_data["competitor"] = competitor
        if not self.invite:
            if cleaned_data["player"] in self.competition.players:
                if self.competition.matchup_type == 2 and self.approved:
                    if cleaned_data.get("competitor", False):
                        competitor = cleaned_data['competitor']
                        if not isinstance(competitor, models.Competitor):
                            competitor = models.Competitor.objects.get(id=competitor)
                        old_competitor = self.competition.get_competitor(cleaned_data["player"])
                        if competitor.id != old_competitor.id:
                            if old_competitor.status == 0:
                                old_competitor.delete()
                            else:
                                old_competitor.players.remove(cleaned_data["player"])
                            competitor.players.add(cleaned_data["player"])
                            competitor.status = 1
                            competitor.save()
                        self.added = True
                else:
                    raise forms.ValidationError(
                        'Player already exists.',
                        code='duplicate'
                    )
        return cleaned_data

    def save(self, commit=True):
        if not self.added:
            cleaned_data = self.cleaned_data
            if cleaned_data['player']:
                params = {"player": cleaned_data["player"],
                          "competition": self.competition}
                if not self.approved:
                    params["invite_type"] = 2
                    params["competitor"] = self.parent
                else:
                    params["invite_type__in"] = [1, 3]
                existing_invites = models.CompetitionInvite.objects.filter(**params)
                if existing_invites.exists():
                    existing_invites.delete()
                    if existing_invites.filter(accepted=True):
                        competitor = self.competition.add_competitor(player=cleaned_data["player"])
                        return competitor
            pending_player = super(AddCompetitorForm, self).save(commit=False)
            pending_player.competition = self.competition
            if self.invite:
                self.invite.send_invitation(self.request)
                pending_player.invite = self.invite
            if self.approved:
                pending_player.invite_type = 1
            else:
                pending_player.invite_type = 2
                pending_player.competitor = self.parent
            pending_player.approved = self.approved

            if commit:
                pending_player.save()
        return self.parent


class CompetitorInviteForm(AddCompetitorForm):
    approved = False


class EditCompetitorForm(MyBaseModelForm):
    seed = forms.ChoiceField(required=False)

    class Meta:
        model = models.Competitor
        fields = ['team_name', 'captain']

    def __init__(self, *args, **kwargs):
        super(EditCompetitorForm, self).__init__(*args, **kwargs)
        self.add_player = False
        competition = self.instance.competition
        if self.instance.competitor_type == 1:
            self.fields.pop('team_name')
            self.fields.pop('captain')
        elif self.instance.status == 0:
            teams = competition.competitors.filter(team_name__isnull=False).values_list("team_name")
            self.fields["team_name"] = forms.ChoiceField(required=False,
                                                         choices=[("", "--------")] + [(team, team) for team in teams])
            self.fields["team_name"].widget.attrs.update({"class": "form-control"})
            self.fields.pop('captain')
        else:
            self.fields["team_name"].required = True
            self.fields['captain'].queryset = self.instance.players
        if competition.competition_type != 3\
                or competition.competition_details.tourney_seeds == 1:
            self.fields.pop('seed')
        else:
            self.fields['seed'].choices = [(x, x) for x in range(1, competition.competitor_set.count() + 1)]
            self.initial.update({"seed": self.instance.seed()})

    def clean(self):
        cleaned_data = super(EditCompetitorForm, self).clean()
        if cleaned_data.get('team_name'):
            teams = self.instance.competition.competitor_set.filter(team_name=cleaned_data['team_name'])
            if self.instance.team_name != cleaned_data["team_name"] and teams.exists():
                if self.instance.players.count() > 1:
                    raise forms.ValidationError(
                        'Team name already exists.',
                        code='duplicate'
                    )
                else:
                    self.add_player = True
                    teams.first().players.add(self.instance.players.first())
        return cleaned_data

    def save(self, commit=True):
        if self.add_player:
            self.instance.delete()
        else:
            instance = super(EditCompetitorForm, self).save()
            seed = self.cleaned_data.get("seed")
            if seed and seed != self.initial.get("seed"):
                instance.add_seed(seed)
            return instance
