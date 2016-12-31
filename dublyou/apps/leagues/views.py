from django.shortcuts import render, HttpResponseRedirect
from . import models
from ..competitions.models import Competition
from .forms import CompetitorForm, TeamForm, BaseCompetitorFormSet, BaseTeamFormSet, LeagueForm
from ..competitions.forms import CreateMatchups
from ...views import ModelFormView, ModelFormSetView, ProfileView


class TeamView(ProfileView):
    model = models.Team
    detail_names = ["team_members", "league", "captain", "max_members", "division"]
    stat_names = []
    tab_names = []


class LeagueView(ProfileView):
    model = models.League
    detail_names = ["league_members", "games", "commissioner", "max_members"]
    stat_names = []
    tab_names = []


class LeagueMemberView(ModelFormSetView):
    def __init__(self, **kwargs):
        super(LeagueMemberView, self).__init__(**kwargs)
        self.competition = None
        self.league = None

    def get_form_kwargs(self):
        form_kwargs = super(LeagueMemberView, self).get_form_kwargs()
        form_kwargs["user"] = self.request.user
        ref_id = self.kwargs['ref_id']
        id_type = self.kwargs['id_type']
        if id_type == "competition":
            self.competition = Competition.object.get(id=ref_id)
            self.league = self.competition.league
        else:
            self.league = models.League.objects.get(id=ref_id)
        form_kwargs['league_id'] = self.league.id


class AddPlayersView(LeagueMemberView):
    model = models.LeagueMember
    form_class = CompetitorForm
    base_formset_class = BaseCompetitorFormSet
    success_url = "/leagues/{league.id}"
    form_title = "Add Players"
    form_action = "leagues/add_players"

    def form_valid(self, formset, redirect=True):
        super(AddPlayersView, self).form_valid(formset, redirect=False)
        if self.kwargs['id_type'] == "competition":
            CreateMatchups(self.competition, self.league)

        if redirect:
            return HttpResponseRedirect(self.get_success_url())


class AddTeamsView(LeagueMemberView):
    model = models.Team
    form_class = TeamForm
    base_formset_class = BaseTeamFormSet
    success_url = "/leagues/add_players/{id_type}/{ref_id}"
    form_title = "Add Teams"
    form_action = "leagues/add_teams"

    def get_success_url(self):
        pass


class NewLeagueView(ModelFormView):
    model = models.League
    form_class = LeagueForm
    success_url = "/leagues/{id}"
    form_title = "New League"
    form_action = "leagues/new"
