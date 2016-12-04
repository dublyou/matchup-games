# -*- coding: utf-8 -*-
from django.shortcuts import render  # , render_to_response
from django.http import HttpResponseRedirect
from . import models
# from django.template.context_processors import csrf
from . import forms
from ..leagues.forms import CompetitorForm, TeamForm, BaseCompetitorFormSet, BaseTeamFormSet
from django.forms.formsets import formset_factory
from django.contrib.auth.decorators import login_required


@login_required
def create_game(request):
    if request.method == 'POST':

        user = request.user

        event_form = forms.CreateGameForm(request.POST.get, user=user)

        if event_form.is_valid():

            cleaned_data = event_form.cleaned_data
            valid_competitors = True
            league, competitor_formset, team_formset = None

            if not event_form.league:
                league = models.League(league_name=event_form.event_name, comp_type=cleaned_data["comp_type"])

                if cleaned_data["comp_type"] == 1:
                    CompetitorFormSet = formset_factory(CompetitorForm, formset=BaseCompetitorFormSet)
                    competitor_formset = CompetitorFormSet(request.POST.get)

                    valid_competitors = competitor_formset.is_valid()

                if cleaned_data["comp_type"] == 2:
                    TeamFormSet = formset_factory(TeamForm, formset=BaseTeamFormSet)
                    team_formset = TeamFormSet(request.POST.get)

                    valid_competitors = team_formset.is_valid()

                    if valid_competitors:
                        teams = {}
                        for team_form in team_formset:
                            teams[team_form.cleaned_data.get("team_name")] = 0

                        CompetitorFormSet = formset_factory(CompetitorForm, formset=BaseCompetitorFormSet)
                        competitor_formset = CompetitorFormSet(request.POST.get, form_kwargs={'teams': teams.keys()})

                        players_per_team = cleaned_data.get("players_per_team")
                        valid_competitors = competitor_formset.is_valid()
                        if valid_competitors:
                            for competitor_form in competitor_formset:
                                teams[competitor_form.cleaned_data.get("team")] += 1

                            valid_competitors = not all(i == players_per_team for i in teams.values())

            if valid_competitors:
                if cleaned_data["event_type"] == 5:
                    OlympicEventFormSet = formset_factory(forms.CreateGameForm)
                    olympic_event_formset = OlympicEventFormSet(request.POST.get)

                    if olympic_event_formset.is_valid():
                        if league:
                            league.save()
                            for competitor_form in competitor_formset:
                                competitor_form.save()

                            if cleaned_data["comp_type"] == 2:
                                for team_form in team_formset:
                                    team_form.save(league)

                        event_form.set_competitors(league)
                        parent_event = event_form.create_event(league=league)

                        for event in olympic_event_formset:
                            event.create_event(parent_event=parent_event)

                        return HttpResponseRedirect('/profile/')
                    else:
                        return "errors"
                else:
                    if league:
                        league.save()
                        for competitor_form in competitor_formset:
                            competitor_form.save()

                        if cleaned_data["comp_type"] == 2:
                            for team_form in team_formset:
                                team_form.save(league)

                    event_form.set_competitors(league)
                    event_form.create_event(league=league)

                    return HttpResponseRedirect('/profile/')
        else:
            return "errors"
    else:
        content = {"navbar": "",
                   "panel": "",
                   "form": ""
                   }

        return render(request, "base.html", content)


