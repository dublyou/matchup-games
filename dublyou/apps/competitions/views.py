# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.http import HttpResponseRedirect
from . import models
from . import forms
from ...views import ProfileView, ModelFormView, ModelFormSetView
from ..leagues.models import League
from django.forms.formsets import formset_factory
from django.contrib.auth.decorators import login_required


@login_required
def new_competition(request):
    if request.method == 'POST':

        user = request.user

        competition_form = forms.CompetitionForm(request.POST.get, user=user)

        if competition_form.is_valid():
            cleaned_data = competition_form.cleaned_data
            event_type = cleaned_data["event_type"]
            valid = True
            event_form = None
            if event_type in range(2, 5):
                if event_type == 2:
                    event_form = forms.SeriesForm(request.POST.get)
                elif event_type == 3:
                    event_form = forms.TournamentForm(request.POST.get)
                elif event_type == 4:
                    event_form = forms.SeasonForm(request.POST.get)
                valid = event_form.is_valid()

            if valid:
                competition = competition_form.save()
                if event_form:
                    event_form.save(competition=competition)

                league = League.objects.create(league_name="Competition " + str(competition.id),
                                               comp_type=cleaned_data["comp_type"],
                                               game_type=cleaned_data["game_type"] or None,
                                               commissioner=user,
                                               dummy_league=True
                                               )
                competition.league = league
                competition.save()

                if event_type == 5:
                    return HttpResponseRedirect('/olympic_events/' + str(competition.id))
                elif cleaned_data["comp_by"] == 1:
                    if cleaned_data["comp_type"] == 2:
                        return HttpResponseRedirect('/add_teams/comp' + str(competition.id))
                    elif cleaned_data["comp_type"] == 1:
                        return HttpResponseRedirect('/add_members/comp' + str(competition.id))
                else:
                    return HttpResponseRedirect('/events/' + str(competition.id))

    form = {
        "title": "New Competition",
        "windows": [
            {"id": "new_competition", "classes": "", "type": "formset",
             "content": [
                 forms.CompetitionForm(),
                 forms.CompetitorInfoForm(user=request.user),
                 forms.SeriesForm(),
                 forms.TournamentForm(),
                 forms.SeasonForm()
             ]
             }
        ],
        "submit_label": "Create"
    }

    content = {"navbar": "",
               "template": "form.html",
               "args": form
               }

    return render(request, "single_content.html", content)


@login_required
def olympic_events(request, comp_id):

    competition = models.Competition.object.filter(id=comp_id, competition_type=5)

    if competition.exists() and competition.get().creator == request.user:
        competition = competition.get()
        EventFormSet = formset_factory(forms.CompetitionForm(user=request.user, olympic_id=comp_id))

        if request.method == 'POST':
            formset = EventFormSet(request.POST.get)

            if formset.is_valid():
                for form in formset:
                    form.save(parent=competition)

                if competition.comp_by == 1:
                    if competition.comp_type == 2:
                        return HttpResponseRedirect('/add_teams/comp' + str(competition.id))
                    elif competition.comp_type == 1:
                        return HttpResponseRedirect('/add_members/comp' + str(competition.id))
                    else:
                        return HttpResponseRedirect('/events/' + str(competition.id))
        else:

            form = {
                "title": "Add Events",
                "windows": [
                    {"id": "olympic_events", "type": "formset", "content": EventFormSet(),
                     "props": ""
                     },
                ],
                "submit_label": "Add Events",
                "submit_props": ""
            }

            content = {"navbar": "",
                       "template": "form.html",
                       "args": form
                       }

            return render(request, "single_content.html", content)
    else:
        return render(request, "404.html")


def events_view(request):
    leagues = request.user.leagues.all()
    events = models.Competition.objects.filter(league__in=leagues)

    nav_tabs = {
        "tabs": [{"id": "tournaments", "label": "Tournaments",
                  "content": {"type": "template", "value": "events_table.html",
                              "args": events.filter(competition_type=3)}},
                 {"id": "seasons", "label": "Seasons",
                  "content": {"type": "template", "value": "events_table.html",
                              "args": events.filter(competition_type=4)}},
                 {"id": "olympics", "label": "Olympics",
                  "content": {"type": "template", "value": "events_table.html",
                              "args": events.filter(competition_type=5)}},
                 ]
    }

    content = {"navbar": "",
               "contents": [
                   {"template": "nav_tabs.html", "args": nav_tabs}
               ]}

    return render(request, "my_base.html", content)


class CompetitonView(ProfileView):
    model = models.Competition
    detail_names = ["competition_type", "game_type", ""]
    stat_names = []
    tab_names = ["schedule", "results", "standings", "bracket", "events", "playoffs"]


class MatchupView(ProfileView):
    model = models.Matchup
    detail_names = ["game_type", "date", "time", "venue", "witness"]
    stat_names = []
    tab_names = []


def detail_view(request, event_id):

    event = models.Competition.objects.get(id=event_id)
    event_type = event.event_type

    if event_type in range(3, 6):
        body_content = [
            {"type": "template", "value": "info_group.html",
             "args": {"label": "Event Type", "value": event.get_event_type_display()}},
            {"type": "template", "value": "info_group.html",
             "args": {"label": "Competitor Type", "value": event.get_comp_type_display()}}
        ]

        nav_tabs = {
            "tabs": [{"id": "upcoming_games", "label": "Upcoming Games",
                      "content": {"type": "template", "value": "events_table.html",
                                  "args": None}},
                     {"id": "results", "label": "Results",
                      "content": {"type": "template", "value": "events_table.html",
                                  "args": None}},
                     ]
        }

        if event_type == 3:
            games = event.game_set.all()

            nav_tabs["tabs"].append({"id": "bracket", "label": "Bracket"})

            if games.count() > 0:
                events = event.competition_set.all()
                
            t_body_content = [
                {"type": "template", "value": "info_group.html",
                 "args": {"label": "Game", "value": event.game_type.game_name}},
                {"type": "template", "value": "info_group.html",
                 "args": {"label": "Tourney Type", "value": event.get_tourney_type_display()}}
            ]
            body_content += t_body_content
        elif event_type == 4:

            nav_tabs["tabs"].extend([{"id": "standings", "label": "Standings"},
                                     {"id": "playoffs", "label": "Playoffs"}
                                     ])

            t_body_content = [
                {"type": "template", "value": "info_group.html",
                 "args": {"label": "Game", "value": event.game_type.game_name}},
                {"type": "template", "value": "info_group.html",
                 "args": {"label": "Season Games", "value": event.season_games}}
            ]
            body_content += t_body_content
        else:
            nav_tabs["tabs"][:0] = [{"id": "events", "label": "Events"}]
            nav_tabs["tabs"].append({"id": "standings", "label": "Standings"})

            t_body_content = [
                {"type": "template", "value": "info_group.html",
                 "args": {"label": "Events", "value": event.num_children}}
            ]
            body_content += t_body_content

        panel = {
            "id": "",
            "classes": "",
            "title": event.event_name,
            "body_classes": "flex-wrap",
            "body": body_content
        }

        content = {"navbar": "",
                   "contents": [
                       {"template": "panel.html", "args": panel},
                       {"template": "nav_tabs.html", "args": nav_tabs}
                   ]}

        return render(request, "my_base.html", content)
