# -*- coding: utf-8 -*-
from django.http import HttpResponseRedirect, HttpResponse, Http404, JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank, TrigramSimilarity
from django.template.loader import render_to_string
from django.db.models.functions import Concat
from django.views.generic import DetailView

from .forms import EditProfileForm
from .permissions import ProfilePermissions
from ...views import ProfileView, EditView, ListView, ObjectPermissionsMixin
from ...constants import COMPETITION_TYPES
from ...models import *
from invitations.adapters import get_invitations_adapter


@login_required
def get_profile(request):
    user = request.user
    if user.is_authenticated():
        return HttpResponseRedirect(user.profile.get_absolute_url())


class PlayerProfileView(ProfileView):
    model = Profile
    permission_logic = ProfilePermissions
    details = ["height__string", "weight", "age", "current_location",
               "teams__list", "leagues__list"]
    stats = ["player__record", "player__team_record"]
    tabs = [
        {"name": "my_competitions",
         "label": "Competitions",
         "template": "competitions"},
        {"name": "upcoming_matchups",
         "template": "matchup_competitors"},
        {"name": "matchup_results",
         "template": "matchup_competitors"},
        {"name": "player_invitations",
         "label": "Invitations",
         "template": "invitations",
         "badge": "invite_count"}
    ]
    toolbar = [
        {"type": "dropdown",
         "classes": "ajax-link",
         "btns": [{"name": "new_competition"}]
                 + [{"name": "new_competition",
                     "label": y,
                     "kwargs": {"field": "competition_type", "competition_type": str(x)}} for x, y in
                    COMPETITION_TYPES]},
        {"classes": "hidden-xs ajax-link",
         "btns": [{"name": "new_league"},
                  {"name": "new_game"},
                  ]
         },
        {"classes": "",
         "btns": [{"name": "send-invite",
                   "glyph": "envelope"}
                  ]
         },
        {"classes": "ajax-link",
         "btns": [{"name": "edit_profile",
                   "glyph": "edit",
                   "kwargs": {"pk": "object__id"}}
                  ]
         }
    ]


class EditProfileView(EditView):
    model = Profile
    form_class = EditProfileForm
    success_url = "/profile/{id}"
    form_title = "Edit Profile"
    permission_logic = ProfilePermissions
    permission_required = "edit_profile"
    login_required = True

edit_profile = EditProfileView.as_view()


class UpcomingMatchupsView(ListView):
    template_name = "base.html"
    include_template_name = "matchup_competitors.html"
    model = Profile
    permission_logic = ProfilePermissions
    object_list_attr = "player__upcoming_matchups"

upcoming_matchups = UpcomingMatchupsView.as_view()


class MatchupResultsView(ListView):
    template_name = "base.html"
    include_template_name = "matchup_competitors.html"
    model = Profile
    permission_logic = ProfilePermissions
    object_list_attr = "player__matchup_results"

matchup_results = MatchupResultsView.as_view()


class CompetitionsView(ListView):
    template_name = "base.html"
    include_template_name = "tabs/competitions.html"
    model = Profile
    permission_logic = ProfilePermissions
    list_model = Competition
    object_list_attr = "competitors"


my_competitions = CompetitionsView.as_view()


class PlayerInvitationsView(ObjectPermissionsMixin, DetailView):
    template_name = "base.html"
    include_template_name = "invitations.html"
    model = Profile
    permission_logic = ProfilePermissions
    permission_required = "view"
    login_required = True

    def get_template_names(self):
        self.template_name = self.kwargs.get("template_name") or self.template_name
        return super(PlayerInvitationsView, self).get_template_names()

player_invitations = PlayerInvitationsView.as_view()


@login_required
def profile_search(request):
    if request.is_ajax():
        search_term = request.GET.get('search_term')

        if False:
            vector = SearchVector('user__email', weight='A') + SearchVector('user__first_name',
                                                                            'user__last_name', weight='B')
            query = SearchQuery(search_term)
            search_results = Profile.objects\
                .annotate(rank=SearchRank(vector, query)) \
                .filter(rank__gte=0.1).order_by('rank').all()
        else:
            search_results = Profile.objects\
                .annotate(search_field=Concat("user__email", "user__first_name", Value(" "), "user__last_name"))\
                .annotate(similarity=TrigramSimilarity('search_field', search_term))\
                .filter(similarity__gt=0.2).order_by('-similarity').all()

        return JsonResponse(render_to_string("profile/profile_list.html", {"profiles": search_results}),
                            safe=False)
    else:
        raise Http404
