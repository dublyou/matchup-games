# -*- coding: utf-8 -*-
import json

from django.core import serializers
from django.shortcuts import reverse
from django.http import HttpResponseRedirect
from django.views.generic import FormView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.template.loader import render_to_string

from invitations.forms import InviteForm
from allauth.socialaccount.models import SocialApp

from . import models
from . import forms
from ..youtube.models import MatchupVideo
from ..youtube.forms import MatchupVideoForm
from .permissions import CompetitionPermissions, MatchupPermissions, CompetitorPermissions
from ...views import ProfileView, ActionView, EditView, NewObjectView, JsonResponse, \
    NewChildObjectView, ManageView, ListView, ObjectPermissionsMixin, UpdateView, DetailView


@login_required
def get_competitions(request):
    user = request.user
    if user.is_authenticated():
        return HttpResponseRedirect("/profile/{}/competitions/".format(user.profile.id))


class NewCompetitionView(LoginRequiredMixin, NewObjectView):
    form_title = "New Competition"
    form_id = None
    form_action = None
    submit_label = "Create"
    form_class = forms.CompetitionForm
    success_url = "/competitions/{id}/"

    def get_initial(self):
        initial = super(NewCompetitionView, self).get_initial()
        kwargs = self.kwargs
        field = kwargs.get("field")
        if field:
            initial.update({field: kwargs.get(field)})
        return initial

new_competition = NewCompetitionView.as_view()


class EditCompetitionView(EditView):
    model = models.Competition
    permission_logic = CompetitionPermissions
    permission_required = "edit_competition"
    login_required = True
    form_class = forms.EditCompetitionForm
    form_title = "Edit Competition"

edit_competition = EditCompetitionView.as_view()


class AddEventView(NewChildObjectView):
    model = models.Competition
    permission_required = "manage_events"
    permission_logic = CompetitionPermissions
    form_class = forms.CompetitionForm

add_event = AddEventView.as_view()


class ManageEventsView(ManageView):
    model = models.Competition
    inline_model = models.Competition
    permission_logic = CompetitionPermissions
    permission_required = "manage_events"
    form_title = "Manage Events"
    form_class = forms.EditCompetitionForm
    success_url = "competitions/{id}/"
    include_template_name = "tabs/manage_events.html"
    add_form_class = forms.CompetitionForm
    fk_name = "parent"

manage_events = ManageEventsView.as_view()


class CompetitionView(ProfileView):
    model = models.Competition
    permission_logic = CompetitionPermissions
    details = ["competition_type__display", "competition_details", "game", "events__list",
               "creator__btn", "competitors__list", "players__list", "parent__btn",
               "status__display", "date__formatted", "time__formatted"]
    stats = []
    tabs = [
        {"name": "competition_upcoming_matchups",
         "template": "matchups",
         "label": "Upcoming Matchups"},
        {"name": "competition_matchup_results",
         "template": "matchups",
         "label": "Matchup Results"},
        {"name": "competition_bracket",
         "label": "Bracket"},
        {"name": "competition_standings",
         "label": "Standings",
         "template": "standings"},
        {"name": "manage_events"},
        {"name": "manage_competitors"},
        {"name": "manage_competition_signup",
         "label": "Manage Sign Up",
         "template": "manage_signup"}
    ]
    toolbar = [
        {"classes": "ajax-link",
         "btns": [{"name": "create_matchups",
                   "kwargs": {"pk": "object__id"}},
                  {"name": "join_competition",
                   "kwargs": {"pk": "object__id"}},
                  {"name": "competition_withdraw",
                   "label": "Withdraw",
                   "kwargs": {"pk": "object__id"}},
                  ]
         },
        {"classes": "ajax-link",
         "btns": [{"name": "edit_competition",
                   "kwargs": {"pk": "object__id"},
                   "glyph": "edit"},
                  {"name": "delete_competition",
                   "kwargs": {"pk": "object__id"},
                   "glyph": "trash"},
                  ]
         }
    ]

    def get_context_data(self, **kwargs):
        ctx = super(CompetitionView, self).get_context_data(**kwargs)
        if self.object.competition_type == 3:
            ctx["scripts"] = [{"name": "js/bracketv2.js"},
                              {"name": "js/competition_bracket.js"}]
        return ctx


class DeleteCompetition(ActionView):
    model = models.Competition
    permission_logic = CompetitionPermissions
    permission_required = "delete_competition"
    login_required = True
    success_url = "/profile/"
    verb = "delete"

    def run_process(self, request, *args, **kwargs):
        instance = self.object
        if instance.status > 2:
            instance.status = 7
            instance.save()
        else:
            instance.delete()

delete_competition = DeleteCompetition.as_view()


class CreateCompetitionMatchups(ActionView):
    model = models.Competition
    permission_logic = CompetitionPermissions
    permission_required = "create_matchups"
    login_required = True
    success_url = "/competitions/{id}/"
    verb = "create"

    def get_warning(self):
        warning = super(CreateCompetitionMatchups, self).get_warning()
        warnings = [warning]
        if self.object.competitors.filter(status=0).exists():
            warnings.insert(0, "If you move forward any pending competitors will be deleted.")
        if self.object.invites.exists():
            warnings.insert(0, "If you move forward any pending invitations will expire.")
        if self.object.matchups.exists():
            warnings.insert(0, "If you move forward existing matchups will be deleted.")
        return " ".join(warnings)

    def get_errors(self):
        errors = []
        min_competitors = 2 if self.object.competition_type != 3 else 3
        if self.object.competitors.filter(status=1).count() < min_competitors:
            errors.append("Must have at least {} competitors.".format(min_competitors))
        if self.object.status > 2:
            errors.append("Your competition is already in progress.")
        return errors

    def run_process(self, request, *args, **kwargs):
        self.object.create_matchups()

create_matchups = CreateCompetitionMatchups.as_view()


class MatchupView(ProfileView):
    model = models.Matchup
    permission_logic = MatchupPermissions
    details = ["winner__btn", "status__display", "competition__link", "game__link",
               "date__formatted", "time__formatted", "venue", "rules", "notes",
               "witness", "competitors__versus"]
    stats = []
    tabs = [{"name": "manage_result"},
            {"name": "matchup_videos",
             "label": "Videos",
             "template": "videos"},
            {"name": "box_score"},
            {"name": "lineup"},
            ]
    toolbar = [
        {"classes": "",
         "btns": [{"name": "add_witness",
                   "kwargs": {"pk": "id"}},
                  {"name": "approve_witness",
                   "kwargs": {"pk": "id"}},
                  ]
         },
        {"classes": "ajax-link",
         "btns": [{"name": "upload_matchup_video",
                   "label": "Upload Video",
                   "kwargs": {"pk": "object__id"},
                   "glyph": "upload"},
                  {"name": "edit_matchup",
                   "kwargs": {"pk": "object__id"},
                   "glyph": "edit"}
                  ]
         }
    ]


class EditMatchupView(EditView):
    model = models.Matchup
    permission_logic = MatchupPermissions
    permission_required = "edit_matchup"
    login_required = True
    form_class = forms.MatchupForm
    form_title = "Edit Matchup"

edit_matchup = EditMatchupView.as_view()


class ManageResultView(ManageView):
    model = models.Matchup
    inline_model = models.MatchupCompetitor
    permission_logic = MatchupPermissions
    permission_required = "manage_result"
    login_required = True
    form_title = "Manage Result"
    form_class = forms.MatchupResultForm
    formset_class = forms.MatchupResultFormset
    success_url = "/competitions/matchups/{id}/"
    include_template_name = "tabs/manage_result.html"
    can_delete = False

manage_result = ManageResultView.as_view()


class UpcomingMatchupsView(ListView):
    template_name = "base.html"
    include_template_name = "matchups.html"
    model = models.Competition
    permission_logic = CompetitionPermissions
    object_list_attr = "upcoming_matchups"

upcoming_matchups = UpcomingMatchupsView.as_view()


class MatchupResultsView(ListView):
    template_name = "base.html"
    include_template_name = "matchups.html"
    model = models.Competition
    permission_logic = CompetitionPermissions
    object_list_attr = "matchup_results"

matchups_results = MatchupResultsView.as_view()


class StandingsView(ListView):
    template_name = "base.html"
    include_template_name = "standings.html"
    model = models.Competition
    permission_logic = CompetitionPermissions
    object_list_attr = "results"

    def get_object_list(self):
        if self.object_list_attr:
            getattr(self.object, self.object_list_attr)
            return getattr(self.object, self.object_list_attr)

competition_standings = StandingsView.as_view()


class BracketView(ListView):
    template_name = "base.html"
    include_template_name = "competition_bracket.html"
    model = models.Competition
    permission_logic = CompetitionPermissions
    object_list_attr = "competitors"

    def get_object_list(self):
        object_list = super(BracketView, self).get_object_list()
        competitors = []
        for obj in object_list:
            competitor_btn = render_to_string("profile/profile_button.html", {"args": obj})
            competitors.append(str(competitor_btn))
        return json.dumps(competitors)

    def get_context_data(self, **kwargs):
        ctx = super(BracketView, self).get_context_data(**kwargs)
        winners = self.object.matchup_competitors.filter(place=1)
        winners_data = {}
        for winner in winners:
            competitor_btn = render_to_string("profile/profile_button.html", {"args": winner.competitor})
            winners_data[winner.matchup.child_num] = {"name": competitor_btn,
                                                      "seed": winner.seed}
        losers = self.object.matchup_competitors.filter(place=2)
        losers_data = {}
        for loser in losers:
            competitor_btn = render_to_string("profile/profile_button.html", {"args": loser.competitor})
            losers_data[loser.matchup.child_num] = {"name": competitor_btn,
                                                    "seed": loser.seed}

        ctx["winners"] = json.dumps(winners_data)
        ctx["losers"] = json.dumps(losers_data)
        return ctx

competition_bracket = BracketView.as_view()


class CompetitorView(ProfileView):
    model = models.Competitor
    permission_logic = CompetitorPermissions
    details = ["competition__link", "captain__btn", "players__list"]
    stats = ["record"]
    tabs = [
        {"name": "competitor_upcoming_matchups",
         "template": "matchup_competitors",
         "label": "Upcoming Matchups"},
        {"name": "competitor_matchup_results",
         "template": "matchup_competitors",
         "label": "Matchup Results"},
        {"name": "competitor_manage_players",
         "template": "manage_players",
         "label": "Manage Players"}
    ]
    toolbar = [
        {"classes": "",
         "btns": [{"name": "join_competitor",
                   "kwargs": {"pk": "object__id"}}
                  ]
         },
        {"classes": "",
         "btns": [{"name": "edit_competitor",
                   "kwargs": {"pk": "object__id"},
                   "glyph": "edit"}
                  ]
         }
    ]

competitor = CompetitorView.as_view()


class EditCompetitorView(EditView):
    model = models.Competitor
    permission_logic = CompetitorPermissions
    permission_required = "edit_competitor"
    login_required = True
    form_class = forms.EditCompetitorForm
    form_title = "Edit Competitor"

edit_competitor = EditCompetitorView.as_view()


class CompetitorUpcomingMatchupsView(ListView):
    template_name = "base.html"
    include_template_name = "matchup_competitors.html"
    model = models.Competitor
    permission_logic = CompetitorPermissions
    object_list_attr = "upcoming_matchups"

competitor_upcoming_matchups = CompetitorUpcomingMatchupsView.as_view()


class CompetitorMatchupResultsView(ListView):
    template_name = "base.html"
    include_template_name = "matchup_competitors.html"
    model = models.Competitor
    permission_logic = CompetitorPermissions
    object_list_attr = "matchup_results"

competitor_matchups_results = CompetitorMatchupResultsView.as_view()


class ManageCompetitorsView(ManageView):
    model = models.Competition
    inline_model = models.Competitor
    permission_logic = CompetitionPermissions
    permission_required = "manage_competitors"
    form_title = "Manage Competitors"
    form_class = forms.EditCompetitorForm
    success_url = "/competitions/{id}/"
    include_template_name = "tabs/manage_competitors.html"
    add_form_class = forms.AddCompetitorForm
    can_delete = True

manage_competitors = ManageCompetitorsView.as_view()


class ManagePlayersView(ObjectPermissionsMixin, DetailView):
    model = models.Competitor
    permission_logic = CompetitorPermissions
    permission_required = "competitor_manage_players"
    login_required = True
    template_name = "base.html"
    include_template_name = "tabs/manage_players.html"
    add_form_class = forms.CompetitorInviteForm

    def get_template_names(self):
        self.template_name = self.kwargs.get("template_name") or self.template_name
        return super(ManagePlayersView, self).get_template_names()

    def get_context_data(self, **kwargs):
        ctx = super(ManagePlayersView, self).get_context_data(**kwargs)
        ctx["args"] = {"add_form": self.add_form_class(parent=self.object),
                       "object_type": "competitor"}
        ctx["template"] = self.include_template_name
        return ctx

competitor_manage_players = ManagePlayersView.as_view()


class ManageCompetitionSignUpView(UpdateView):
    model = models.Competition
    include_template_name = "tabs/manage_signup.html"
    permission_logic = CompetitionPermissions
    permission_required = "manage_competition_signup"
    form_title = "Manage Competition Sign Up"
    form_class = forms.CompetitionSignUpForm
    success_url = "/competitions/{id}/"
    template_name = "base.html"

    def get_template_names(self):
        self.template_name = self.kwargs.get("template_name") or self.template_name
        return super(ManageCompetitionSignUpView, self).get_template_names()

    def get_context_data(self, **kwargs):
        ctx = super(ManageCompetitionSignUpView, self).get_context_data(**kwargs)
        ctx["template"] = self.include_template_name
        ctx["facebook_app"] = SocialApp.objects.filter(provider="facebook").first()
        return ctx

manage_competition_signup = ManageCompetitionSignUpView.as_view()


class MatchupVideoUploadView(NewChildObjectView):
    model = models.Matchup
    permission_logic = MatchupPermissions
    form_class = MatchupVideoForm
    form_title = "Upload Video"
    submit_label = "Upload"
    permission_required = "upload_matchup_video"
    template_name = "base.html"

matchup_video_upload = MatchupVideoUploadView.as_view()


class MatchupVideosView(ListView):
    template_name = "base.html"
    include_template_name = "videos.html"
    model = models.Matchup
    permission_logic = MatchupPermissions
    object_list_attr = "videos"

matchup_videos = MatchupVideosView.as_view()


class CompetitionInviteView(NewChildObjectView):
    model = models.Competition
    permission_logic = CompetitionPermissions
    form_class = forms.AddCompetitorForm
    permission_required = "manage_competitors"
    template_name = "base.html"

competition_invite = CompetitionInviteView.as_view()


class CompetitorInviteView(NewChildObjectView):
    model = models.Competitor
    permission_logic = CompetitorPermissions
    permission_required = "competitor_invite"
    form_class = forms.CompetitorInviteForm
    template_name = "base.html"

competitor_invite = CompetitorInviteView.as_view()


class JoinCompetition(ActionView):
    model = models.Competition
    permission_logic = CompetitionPermissions
    permission_required = "join_competition"
    login_required = True
    success_url = "/profile/"
    verb = "join"

    def get_errors(self):
        errors = []
        competition = self.object
        player = self.request.user.profile
        if player in competition.players:
            errors.append("You have already joined this competition.")
        invites = competition.invites.filter(player=player)
        if invites.filter(invite_type=3).exists() and not invites.filter(invite_type=1).exists():
            errors.append(
                "You have already requested to join this competition. Please wait for the creator to approve your request."
            )
        if competition.status > 2:
            errors.append("You cannot join the competition because it has already started.")
        return errors

    def run_process(self, request, *args, **kwargs):
        competition = self.object
        player = request.user.profile
        invites = models.CompetitionInvite.objects.filter(player=player,
                                                          competition=competition,
                                                          invite_type=1)
        if invites.exists():
            invite = invites.first()
            invite.accept()
        else:
            invite, created = models.CompetitionInvite.objects.get_or_create(player=player,
                                                                             competition=competition,
                                                                             invite_type=3)
            if created:
                signup = getattr(competition, "signup_page", None)
                if signup and not signup.key_expired():
                    invite.invite_type = 3
                    invite.save()
                else:
                    invite.delete()
                    return True
                invite.accept()

join_competition = JoinCompetition.as_view()


class JoinCompetitor(ActionView):
    model = models.Competition
    permission_logic = CompetitorPermissions
    permission_required = "join_competitor"
    login_required = True
    success_url = "/profile/"
    verb = "join"

    def get_errors(self):
        errors = []
        instance = self.object
        competition = instance.competition
        player = self.request.user.profile
        if player in competition.players:
            errors.append("You have already joined this competition.")
        if competition.status > 2:
            errors.append("You cannot join the competition because it has already started.")
        return errors

    def run_process(self, request, *args, **kwargs):
        instance = self.object
        player = request.user.profile
        invites = instance.competitor_invites.filter(player=player)
        if invites.exists():
            invite = invites.first()
            invite.accept()

join_competitor = JoinCompetitor.as_view()


class CompetitionSignupView(CompetitionView, FormView):
    model = models.Competition
    template_name = 'tabs/signup.html'
    form_class = InviteForm
    permission_logic = CompetitionPermissions
    permission_required = "competition_signup"
    login_required = False

    def get_context_data(self, **kwargs):
        ctx = super(CompetitionSignupView, self).get_context_data(**kwargs)
        if "form" in kwargs:
            ctx["form"] = kwargs["form"]
        if self.request.user.is_authenticated() and self.permissions.has_perm("join_competition"):
            ctx["join_url"] = reverse("join_competition", kwargs={"pk": self.kwargs["pk"]})
        return ctx

    def form_valid(self, form):
        email = form.cleaned_data["email"]

        try:
            invite = form.save(email)
            invite.inviter = self.request.user
            invite.save()
            invite.send_invitation(self.request)
            models.CompetitionInvite.create(competition=self.object,
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
        signup = models.CompetitionSignUpPage.objects.filter(verification_key=kwargs["key"], competition=self.object)
        # No signup was found.
        if signup.exists():
            signup = signup.get()
            # The key was expired.
            if signup.key_expired():
                return HttpResponseRedirect("/")
        else:
            return HttpResponseRedirect("/")
        return super(CompetitionSignupView, self).dispatch(request, *args, **kwargs)

competition_signup = CompetitionSignupView.as_view()


class WithdrawFromCompetition(ActionView):
    model = models.Competition
    permission_logic = CompetitionPermissions
    permission_required = "competition_withdraw"
    login_required = True
    success_url = "/profile/"
    verb = "withdraw"
    past_verb = "withdrew"

    def get_errors(self):
        errors = []
        competition = self.object
        if competition.status > 2:
            errors.append("You cannot withdraw from the competition because it has already started.")
        return errors

    def run_process(self, request, *args, **kwargs):
        competition = self.object
        player = request.user.profile
        c = competition.get_competitor(player)
        if c:
            if c.competitor_type == 1:
                c.delete()
            else:
                c.players.remove(player)
                if c.captain == player:
                    c.captain = None
                    c.save()

competition_withdraw = WithdrawFromCompetition.as_view()


class AcceptCompetitionInvite(ActionView):
    model = models.Competition
    permission_logic = CompetitionPermissions
    permission_required = "accept_competition_invite"
    login_required = True
    success_url = "/profile/"
    verb = "accept"

    def get_errors(self):
        errors = []
        competition = self.object
        if competition.status > 2:
            errors.append("You cannot accept the competition invitation because it has already started.")
        return errors

    def run_process(self, request, *args, **kwargs):
        pending_invite = request.user.profile.competition_invites.filter(pk=kwargs["pk2"])
        if pending_invite.exists():
            pending_invite.get().accept()
        return True

accept_competition_invite = AcceptCompetitionInvite.as_view()


class ApproveCompetitionInvite(ActionView):
    model = models.Competition
    success_url = "/competitions/{id}/"
    permission_logic = CompetitionPermissions
    permission_required = "manage_competitors"
    login_required = True
    verb = "approve"

    def get_errors(self):
        errors = []
        competition = self.object
        if competition.status > 2:
            errors.append("You cannot approve the competition invitation because it has already started.")
        return errors

    def run_process(self, request, *args, **kwargs):
        competition = self.object
        pending_member = competition.invites.filter(pk=kwargs["pk2"])
        if pending_member.exists():
            pending_member.get().approve()
        return True

approve_competition_invite = ApproveCompetitionInvite.as_view()


class DeleteCompetitionInvite(ActionView):
    model = models.Competition
    success_url = "/competitions/{id}/"
    permission_logic = CompetitionPermissions
    permission_required = "manage_competitors"
    login_required = True
    verb = "delete"

    def run_process(self, request, *args, **kwargs):
        competition = self.object
        pending_member = competition.invites.filter(pk=kwargs["pk2"])
        if pending_member.exists():
            pending_member.get().delete()
        return True

delete_competition_invite = DeleteCompetitionInvite.as_view()
