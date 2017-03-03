from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from django.views.generic import DeleteView, FormView

from invitations.forms import InviteForm
from allauth.socialaccount.models import SocialApp

from . import models
from .forms import AddPlayerForm, EditPlayerForm, TeamForm,\
    AddTeamPlayerForm, EditTeamPlayerForm, LeagueForm, LeagueSignUpForm
from ...views import LoginRequiredMixin, NewObjectView, NewChildObjectView,\
    ObjectPermissionsMixin, ProfileView, ManageView, AjaxableResponseMixin, \
    ListView, UpdateView, EditView, ActionView
from .permissions import LeaguePermissions, TeamPermissions
from ..competitions.models import Competition, MatchupCompetitor


class NewLeagueView(LoginRequiredMixin, NewObjectView):
    model = models.League
    form_class = LeagueForm
    success_url = "/leagues/{id}/"
    form_title = "New League"

new_league = NewLeagueView.as_view()


class EditLeagueView(EditView):
    model = models.League
    permission_logic = LeaguePermissions
    permission_required = "edit_league"
    form_class = LeagueForm
    form_title = "Edit League"

edit_league = EditLeagueView.as_view()


class LeagueView(ProfileView):
    model = models.League
    permission_logic = LeaguePermissions
    details = ["location", "commissioner__link", "privacy_type__display",
               "matchup_type__display", "max_members", "games__list", "players__list"]
    stats = []
    tabs = [
        {"name": "league_competitions",
         "template": "competitions",
         "label": "Competitions"},
        {"name": "manage_teams"},
        {"name": "league_manage_players",
         "template": "manage_players",
         "label": "Manage Players"},
        {"name": "manage_league_signup",
         "label": "Manage Sign Up",
         "template": "manage_signup"}
    ]
    toolbar = [
        {"classes": "",
         "btns": [{"name": "new_competition",
                   "kwargs": {"field": "league", "league": "object__id"}},
                  {"name": "join_league",
                   "kwargs": {"pk": "object__id"}},
                  {"name": "league_withdraw",
                   "label": "Withdraw",
                   "kwargs": {"pk": "object__id"}},
                  ]
         },
        {"classes": "",
         "btns": [{"name": "edit_league",
                   "kwargs": {"pk": "object__id"},
                   "glyph": "edit"},
                  {"name": "delete_league",
                   "kwargs": {"pk": "object__id"},
                   "glyph": "trash"},
                  ]
         }
    ]


class DeleteLeague(ActionView):
    model = models.League
    permission_logic = LeaguePermissions
    permission_required = "delete_league"
    login_required = True
    success_url = "/profile/"

    def run_process(self, request, *args, **kwargs):
        instance = self.object
        if instance.status > 2:
            instance.status = 7
            instance.save()
        else:
            instance.delete()

delete_league = DeleteLeague.as_view()


class LeagueCompetitionsView(ListView):
    template_name = "base.html"
    include_template_name = "competitions.html"
    model = models.League
    permission_logic = LeaguePermissions
    object_list_attr = 'competitions'

league_competitions = LeagueCompetitionsView.as_view()


class TeamView(ProfileView):
    model = models.Team
    permission_logic = TeamPermissions
    details = ["captain__link", "players__list", "division", "league__link", "commissioner", "max_members"]
    stats = []
    tabs = [
        {"name": "team_upcoming_matchups",
         "template": "matchup_competitors",
         "label": "Upcoming Matchups"},
        {"name": "team_matchup_results",
         "template": "matchup_competitors",
         "label": "Matchup Results"},
        {"name": "team_competitions",
         "template": "competitions",
         "label": "Competitions"},
        {"name": "manage_team_players",
         "label": "Manage Players"},
    ]
    toolbar = [
        {"classes": "",
         "btns": [{"name": "edit_team",
                   "kwargs": {"pk": "object__id"},
                   "glyph": "edit"},
                  {"name": "join_team",
                   "kwargs": {"pk": "object__id"}}
                  ]
         }
    ]


class EditTeamView(EditView):
    model = models.Team
    permission_logic = TeamPermissions
    permission_required = "edit_team"
    form_class = TeamForm
    form_title = "Edit Team"

edit_team = EditTeamView.as_view()


class ManageTeamsView(ManageView):
    model = models.League
    inline_model = models.Team
    permission_logic = LeaguePermissions
    permission_required = "edit_team"
    form_title = "Manage Teams"
    form_class = TeamForm
    success_url = "/leagues/{pk}/"
    include_template_name = "tabs/manage_teams.html"
    add_form_class = TeamForm

manage_teams = ManageTeamsView.as_view()


class LeagueManagePlayersView(ManageView):
    model = models.League
    inline_model = models.LeaguePlayer
    permission_logic = LeaguePermissions
    permission_required = "manage_players"
    form_title = "Manage Players"
    form_class = EditPlayerForm
    success_url = "/leagues/{pk}/"
    include_template_name = "tabs/manage_players.html"
    add_form_class = AddPlayerForm

league_manage_players = LeagueManagePlayersView.as_view()


class TeamManagePlayersView(LeagueManagePlayersView):
    model = models.Team
    permission_logic = TeamPermissions
    permission_required = "team_manage_players"
    form_class = EditTeamPlayerForm
    success_url = "leagues/team/{pk}/"
    add_form_class = AddTeamPlayerForm

team_manage_players = TeamManagePlayersView.as_view()


class LeagueChildObjectView(NewChildObjectView):
    model = models.League
    permission_logic = LeaguePermissions
    template_name = "base.html"


class LeagueInviteView(LeagueChildObjectView):
    form_class = AddPlayerForm
    permission_required = "league_invite"

league_invite = LeagueInviteView.as_view()


class TeamInviteView(LeagueChildObjectView):
    model = models.Team
    form_class = AddTeamPlayerForm
    permission_logic = TeamPermissions
    permission_required = "team_invite"

team_invite = TeamInviteView.as_view()


class AddTeamView(LeagueChildObjectView):
    form_class = TeamForm
    permission_required = "add_team"

add_team = AddTeamView.as_view()


class TeamUpcomingMatchupsView(ListView):
    template_name = "base.html"
    include_template_name = "matchup_competitors.html"
    model = models.Team
    permission_logic = TeamPermissions
    object_list_attr = "team_competitors"
    list_model = MatchupCompetitor
    list_model_filters = {"matchup__status__in": [1, 2]}

team_upcoming_matchups = TeamUpcomingMatchupsView.as_view()


class TeamMatchupResultsView(ListView):
    template_name = "base.html"
    include_template_name = "matchup_competitors.html"
    model = models.Team
    permission_logic = TeamPermissions
    object_list_attr = "team_competitors"
    list_model = MatchupCompetitor
    list_model_filters = {"matchup__status__in": [3, 4]}

team_matchups_results = TeamMatchupResultsView.as_view()


class TeamCompetitionsView(ListView):
    template_name = "base.html"
    include_template_name = "competitions.html"
    model = models.Team
    permission_logic = TeamPermissions
    object_list_attr = 'team_competitions'

team_competitions = TeamCompetitionsView.as_view()


class DeleteTeam(ActionView):
    model = models.Team
    permission_logic = LeaguePermissions
    permission_required = "delete_team"
    login_required = True
    success_url = "/leagues/{id}/"
    verb = "delete"

    def run_process(self, request, *args, **kwargs):
        instance = self.object
        if instance.team_competitors.exists():
            instance.status = 3
            instance.save()
        else:
            instance.delete()

delete_team = DeleteTeam.as_view()


class ManageLeagueSignUpView(UpdateView):
    model = models.League
    include_template_name = "tabs/manage_signup.html"
    permission_logic = LeaguePermissions
    permission_required = "manage_league_signup"
    form_title = "Manage League Sign Up"
    form_class = LeagueSignUpForm
    success_url = "/leagues/{id}/"
    template_name = "base.html"

    def get_template_names(self):
        self.template_name = self.kwargs.get("template_name") or self.template_name
        return super(ManageLeagueSignUpView, self).get_template_names()

    def get_context_data(self, **kwargs):
        ctx = super(ManageLeagueSignUpView, self).get_context_data(**kwargs)
        ctx["template"] = self.include_template_name
        ctx["facebook_app"] = SocialApp.objects.filter(provider="facebook").first()
        return ctx

manage_league_signup = ManageLeagueSignUpView.as_view()


class LeagueSignupView(LeagueView, FormView):
    model = models.League
    template_name = 'tabs/signup.html'
    form_class = InviteForm
    permission_logic = LeaguePermissions
    permission_required = "league_signup"
    login_required = False

    def get_context_data(self, **kwargs):
        ctx = super(LeagueSignupView, self).get_context_data(**kwargs)
        if "form" in kwargs:
            ctx["form"] = kwargs["form"]
        if self.request.user.is_authenticated() and self.permissions.has_perm("join_league"):
            ctx["join_url"] = reverse("join_league", kwargs={"pk": self.kwargs["pk"]})
        return ctx

    def form_valid(self, form):
        email = form.cleaned_data["email"]

        try:
            invite = form.save(email)
            invite.inviter = self.request.user
            invite.save()
            invite.send_invitation(self.request)
            models.LeagueInvite.create(league=self.object,
                                       invite=invite,
                                       invite_type=3)
        except Exception:
            return self.form_invalid(form)
        return self.render_to_response(
            self.get_context_data(
                success_message='%s has been invited' % email))

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        signup = models.LeagueSignUpPage.objects.filter(verification_key=kwargs["key"], league=self.object)
        # No signup was found.
        if signup.exists():
            signup = signup.get()
            # The key was expired.
            if signup.key_expired():
                return HttpResponseRedirect("/")
        else:
            return HttpResponseRedirect("/")
        return super(LeagueSignupView, self).dispatch(request, *args, **kwargs)

league_signup = LeagueSignupView.as_view()


class JoinLeague(ActionView):
    model = models.League
    permission_logic = LeaguePermissions
    permission_required = "join_league"
    login_required = True
    url = "/profile/"
    verb = "join"

    def get_errors(self):
        errors = []
        league = self.object
        player = self.request.user.profile
        if player in league.players:
            errors.append("You have already joined this league.")
        invites = league.invites.filter(player=player)
        if invites.filter(invite_type=3).exists() and not invites.filter(invite_type=1).exists():
            errors.append(
                "You have already requested to join this league. Please wait for the commissioner to approve your request."
            )
        return errors

    def run_process(self, request, *args, **kwargs):
        league = self.object
        player = request.user.profile
        invites = models.LeagueInvite.objects.filter(player=player,
                                                     league=league,
                                                     invite_type=1)
        if invites.exists():
            invite = invites.first()
            invite.accept()
        else:
            invite, created = models.LeagueInvite.objects.get_or_create(player=player,
                                                                        league=league,
                                                                        invite_type=3)
            if created:
                signup = getattr(league, "signup_page", None)
                if signup and not signup.key_expired():
                    invite.invite_type = 3
                    invite.save()
                else:
                    invite.delete()
                    return True
                invite.accept()

join_league = JoinLeague.as_view()


class JoinTeam(ActionView):
    model = models.Team
    permission_logic = TeamPermissions
    permission_required = "join_team"
    login_required = True
    url = "/profile/"
    verb = "join"

    def get_errors(self):
        errors = []
        instance = self.object
        league = instance.league
        player = self.request.user.profile
        if player in league.players:
            errors.append("You have already joined this league.")
        return errors

    def run_process(self, request, *args, **kwargs):
        instance = self.object
        player = request.user.profile
        invites = instance.team_invites.filter(player=player)
        if invites.exists():
            invite = invites.first()
            invite.accept()

join_team = JoinTeam.as_view()


class WithdrawFromLeague(ActionView):
    model = models.League
    permission_logic = LeaguePermissions
    permission_required = "league_withdraw"
    login_required = True
    success_url = "/profile/"
    verb = "withdraw"
    past_verb = "withdrew"

    def run_process(self, request, *args, **kwargs):
        league = self.object
        player = request.user.profile
        league_player = league.league_players.filter(player=player)
        if league_player.exists():
            league_player = league_player.first()
            team = league_player.team
            if team and team.captain == player:
                team = None
                team.save()
            league_player.delete()


league_withdraw = WithdrawFromLeague.as_view()


class AcceptLeagueInvite(ActionView):
    model = models.League
    permission_logic = LeaguePermissions
    permission_required = "accept_league_invite"
    login_required = True
    success_url = "/profile/"
    verb = "accept"

    def get_errors(self):
        errors = []
        league = self.object
        if league.status > 2:
            errors.append("You cannot accept the league invitation because it has already started.")
        return errors

    def run_process(self, request, *args, **kwargs):
        pending_invite = request.user.profile.league_invites.filter(pk=kwargs["pk2"])
        if pending_invite.exists():
            pending_invite.get().accept()
        return True

accept_league_invite = AcceptLeagueInvite.as_view()


class ApproveLeagueInvite(ActionView):
    model = models.League
    success_url = "/leagues/{id}/"
    permission_logic = LeaguePermissions
    permission_required = "manage_players"
    login_required = True
    verb = "approve"

    def get_errors(self):
        errors = []
        league = self.object
        if league.status > 2:
            errors.append("You cannot approve the league invitation because it has already started.")
        return errors

    def run_process(self, request, *args, **kwargs):
        league = self.object
        pending_member = league.invites.filter(pk=kwargs["pk2"])
        if pending_member.exists():
            pending_member.get().approve()
        return True

approve_league_invite = ApproveLeagueInvite.as_view()


class DeleteLeagueInvite(ActionView):
    model = models.League
    success_url = "/leagues/{id}/"
    permission_logic = LeaguePermissions
    permission_required = "manage_players"
    login_required = True
    verb = "delete"

    def run_process(self, request, *args, **kwargs):
        instance = self.object
        pending_member = instance.invites.filter(pk=kwargs["pk2"])
        if pending_member.exists():
            pending_member.get().delete()
        return True

delete_league_invite = DeleteLeagueInvite.as_view()
