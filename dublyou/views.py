# -*- coding: utf-8 -*-
from django.shortcuts import render, render_to_response
from django.http import HttpResponseRedirect
from django.contrib import auth
from django.template.context_processors import csrf
from django.template import RequestContext
from . import forms as myforms
from django.forms.formsets import formset_factory
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect


# pages
def home(request):

    if request.method == "POST":
        form = myforms.SignUpForm(request.POST.get)
        if form.is_valid():
            form.save()
            HttpResponseRedirect('')

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
                            },
                           {"type": "reg",
                            "classes": "navbar-right",
                            "items": [{"label": "Logout", "link": "\logout\\"}]
                            }]
        form = None
    else:
        form = {"title": "Sign Up",
                "id": "sign_up",
                "classes": "pull-right xs-block xs-no-float sm-inline",
                "windows": [{"type": "form",
                             "content": myforms.SignUpForm()}
                            ],
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
                                         "id": "username",
                                         "placeholder": "Email"},
                                        {"type": "password",
                                         "classes": "",
                                         "id": "password",
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


def login(request):
    username = request.POST.get("username", "")
    password = request.POST.get("password", "")
    user = auth.authenticate(username=username, password=password)

    if user is not None:
        auth.login(request, user)
        return HttpResponseRedirect('/profile/')


def logout(request):
    auth.logout(request)
    return HttpResponseRedirect('')


def sign_up(request):
    if request.method == "POST":
        form = myforms.SignUpForm(request.POST.get)
        if form.is_valid():
            form.save()
            HttpResponseRedirect('')


