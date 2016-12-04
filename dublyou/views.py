# -*- coding: utf-8 -*-
from django.shortcuts import render, render_to_response
from django.http import HttpResponseRedirect
from django.contrib import auth
# from django.template.context_processors import csrf
from . import forms as myforms
from django.forms.formsets import formset_factory
from django.contrib.auth.decorators import login_required


# pages
def home(request):

    panel = {"id": "panel-cards",
             "title": "Leaders",
             "classes": "pull-left xs-center-block xs-no-float sm-inline",
             "body_classes": "flex-cards",
             "body_content": [{"type": "template",
                               "value": "panel.html",
                               "args": ""},
                              {"type": "template",
                               "value": "panel.html",
                               "args": ""},
                              {"type": "template",
                               "value": "panel.html",
                               "args": ""}
                              ]
             }
    if request.user.is_authenticated:
        navbar_sections = [{"type": "reg",
                            "classes": "",
                            "items": [{"label": "Profile", "link": "\Profile\\"},
                                      {"label": "Rankings", "link": "\Rankings\\"},
                                      {"label": "About Us", "link": ""},
                                      {"label": "Contact Us", "link": ""}
                                      ]
                            }]
        form = None
    else:
        form = {"title": "Sign Up",
                "id": "sign_up",
                "classes": "pull-right xs-block xs-no-float sm-inline",
                "form_fields": myforms.SignUpForm().as_input_group(),
                "submit_label": "Sign Up"
                }

        navbar_sections = [{"type": "reg",
                            "classes": "",
                            "items": [{"label": "Rankings", "link": ""},
                                     {"label": "About Us", "link": ""},
                                     {"label": "Contact Us", "link": ""}
                                     ]
                            },
                           {"type": "form",
                            "classes": "navbar-right",
                            "members": [{"type": "email",
                                         "classes": "",
                                         "id": "sign_in_email",
                                         "placeholder": "Email"},
                                        {"type": "password",
                                         "classes": "",
                                         "id": "sign_in_password",
                                         "placeholder": "Password"},
                                        {"type": "submit",
                                         "classes": "btn-primary",
                                         "text": "Sign In"}
                                        ]
                            }]

    navbar = {"title": "dublyou",
              "sections": navbar_sections
              }

    content = {"navbar": navbar,
               "panel": panel,
               "form": form
               }

    return render(request, "base.html", content)


def rankings(request):
    content = {}

    return render(request, "home.html", content)


@login_required
def profile_view(request):
    navbar = {"title": "dublyou",
              "sections": [{"type": "reg",
                            "classes": "",
                            "items": [{"label": "About Us", "link": ""},
                                      {"label": "Contact Us", "link": ""}
                                      ]
                            }
                           ]
              }

    content = {"args": {"title": "dublyou",
                        "navbar": navbar}}

    return render(request, "home.html", content)


def home_files(request, filename):
    return render(request, filename, {}, content_type="text/plain")


# form handlers
@login_required
def create_game(request):
    if request.method == 'POST':

        user = request.user

        parent_event_form = myforms.CreateGameForm(request.POST.get, user=user)

        if parent_event_form.is_valid():

            parent_comp_type = parent_event_form.cleaned_data.get("comp_type")

            if parent_comp_type == 1:
                CompetitorFormSet = formset_factory(myforms.CompetitorForm)
                competitor_formset = CompetitorFormSet(request.POST.get, user=user)

                if competitor_formset.is_valid():
                    competitors = []
                    for competitor_form in competitor_formset:
                        competitors.append(competitor_form.cleaned_data.get("competitor"))
            elif parent_comp_type == 2:
                pass
            parent_event_form.set_competitors(competitors)
            parent_event_type = parent_event_form.cleaned_data.get("event_type")

            if parent_event_type == 4:
                OlympicEventFormSet = formset_factory(myforms.OlympicEventForm)

                olympic_event_formset = OlympicEventFormSet(request.POST.get)

                if olympic_event_formset.is_valid():

                    parent_event = parent_event_form.save()

                    for event_form in olympic_event_formset:
                        event_form.save(parent_event)

                    for competitor_form in competitor_formset:
                        competitor_form.save(parent_event)

                    return HttpResponseRedirect('/profile/')
                else:
                    return "errors"
            else:
                parent_event = parent_event_form.save()

                for competitor_form in competitor_formset:
                    competitor_form.save(parent_event)

                return HttpResponseRedirect('/profile/')
        else:
            return "errors"


def auth_view(request):
    username = request.POST.get("username", "")
    password = request.POST.get("password", "")
    user = auth.authenticate(username=username, password=password)

    if user is not None:
        auth.login(request, user)
        return HttpResponseRedirect('/profile/')


def logout_view(request):
    auth.logout(request)
    return HttpResponseRedirect('')

