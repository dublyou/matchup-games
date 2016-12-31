# -*- coding: utf-8 -*-
from django.conf import settings
from django.core.mail import send_mail
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.contrib import auth
from django.forms.formsets import formset_factory
from .forms import ContactForm, MySignupForm
from .apps.player_profile.forms import SignUpForm
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.detail import DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from .constants import USER_NAVBAR
from allauth.account.views import LoginView, SignupView
# from django.contrib.auth.decorators import login_required


class ModelFormView(CreateView):
    template_name = "single_content.html"
    form_title = None
    form_id = None
    form_action = None
    submit_label = "Submit"

    def get_context_data(self, **kwargs):
        ctx = super(ModelFormView, self).get_context_data(**kwargs)
        form_id = self.form_id or self.form_title.lower().replace(" ", "_")
        form = {
            "title": self.form_title,
            "id": form_id,
            "action": self.form_action,
            "type": "form",
            "content": ctx['form'],
            "props": "",
            "submit_label": self.submit_label,
            "submit_props": ""
        }
        ctx["navbar"] = USER_NAVBAR
        ctx["template"] = "form.html"
        ctx["args"] =form

        return ctx


class ModelFormSetView(ModelFormView):
    base_formset_class = None

    def get_form_class(self):
        form_class = super(ModelFormSetView, self).get_form_class()
        formset_class = formset_factory(form_class(**self.get_form_kwargs()), formset=self.base_formset_class)
        return formset_class

    def get_context_data(self, **kwargs):
        ctx = super(ModelFormView, self).get_context_data(**kwargs)
        ctx['args']['type'] = "formset"

    def form_valid(self, formset, redirect=True):
        for form in formset:
            form.save()
        if redirect:
            return HttpResponseRedirect(self.get_success_url())


class ProfileView(LoginRequiredMixin, DetailView):
    template_name = "profile.html"
    detail_names = []
    stat_names = []
    tab_names = []
    toolbar = []
    image_name = "image"

    def get_context_data(self, **kwargs):
        ctx = super(ProfileView, self).get_context_data(**kwargs)
        instance = self.object

        if instance.permissions(self.request.user) == "edit":
            details = {("{}s".format(name[:-5]) if name[-5:] == "_list" else name).replace("_", " "): getattr(instance, name, "")
                       for name in self.detail_names}
            stats = [{name: getattr(instance, name, "")} for name in self.stat_names]

            ctx["navbar"] = USER_NAVBAR
            ctx["toolbar"] = self.toolbar
            ctx["header"] = {"name": str(instance),
                             "details": details,
                             "stats": stats,
                             "image": getattr(instance, self.image_name, "").url}
            ctx["navtabs"] = [{"id": name,
                               "label": name.title().replace("_", " "),
                               "content": getattr(instance, "{}_page".format(name), "")}
                              for name in self.tab_names]
        return ctx


class EditView(LoginRequiredMixin, UpdateView):
    template_name = "single_content.html"
    form_title = None
    form_id = None
    form_action = None
    submit_label = "Save"

    def get_context_data(self, **kwargs):
        ctx = super(EditView, self).get_context_data(**kwargs)
        form_id = self.form_id or self.form_title.lower().replace(" ", "_")
        form = {
            "title": self.form_title,
            "id": form_id,
            "action": self.form_action,
            "type": "form",
            "content": ctx['form'],
            "props": "",
            "submit_label": self.submit_label,
            "submit_props": ""
        }
        ctx["navbar"] = USER_NAVBAR
        ctx["template"] = "form.html"
        ctx["args"] = form

        return ctx


# pages
def home(request):

    if request.method == "POST":
        form = SignUpForm(request.POST.get)
        if form.is_valid():
            form.save()
            HttpResponseRedirect('')

    if request.user.is_authenticated:

        form = None
        navbar = USER_NAVBAR
    else:
        form = {"title": "Sign Up",
                "id": "sign_up",
                "classes": "",
                "windows": [{"type": "form",
                             "content": MySignupForm()}
                            ],
                "submit_label": "Sign Up"
                }
        navbar = {"brand": "dublyou",
                  "sections": [
                      {"type": "reg",
                       "classes": "",
                       "members": [{"label": "Home", "link": "/home/", "classes": "active"},
                                   {"label": "Rankings", "link": "/rankings/"}
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
                  }

    content = {"navbar": navbar,
               "template": "grid.html",
               "contents": [
                   {"template": "form.html",
                    "args": form,
                    "row": "new",
                    "col": [12, 8, 8, 7]
                    },
                   {"template": "twitter_profile.html",
                    "args": "",
                    "col": [12, 4, 4, 5]
                    }],
               }

    return render(request, "my_base.html", content)


def home_files(request, filename):
    return render(request, filename, {}, content_type="text/plain")


def bracket_builder(request):
    content = {"title": "Bracket Builder",
               "navbar": None
               }
    return render(request, "bracket_builder.html", content)


class MySignupView(SignupView):
    template_name = "single_content.html"
    form_class = MySignupForm


def sign_in(request):
    username = request.POST.get("username", "")
    password = request.POST.get("password", "")
    user = auth.authenticate(username=username, password=password)

    if user is not None:
        auth.login(request, user)
        return HttpResponseRedirect('/profile/')
    else:
        form = {
            "title": "Send Us A Message",
            "windows": [
                {"id": "sign_in", "classes": "", "type": "form",
                 "content": ""
                 }
            ],
            "submit_label": "Sign In"
        }
        context = {
            "title": "Sign In",
            "template": "form.html",
            "args": form
        }

        return render(request, "single_content.html", context)


def sign_out(request):
    auth.logout(request)
    return HttpResponseRedirect('')


def contact(request):
    title = 'Contact Us'
    form = ContactForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            # for key, value in form.cleaned_data.iteritems():
            # 	print key, value
            # 	#print form.cleaned_data.get(key)
            form_email = form.cleaned_data.get("email")
            form_message = form.cleaned_data.get("message")
            form_full_name = form.cleaned_data.get("full_name")
            # print email, message, full_name
            subject = 'Site contact form'
            from_email = settings.EMAIL_HOST_USER
            to_email = [from_email, 'jgriffin@matchup-games.com']
            contact_message = "{}: {} via {}".format(
                form_full_name,
                form_message,
                form_email)
            some_html_message = """
                                <h1>hello</h1>
                                """
            send_mail(subject,
                      contact_message,
                      from_email,
                      to_email,
                      html_message=some_html_message,
                      fail_silently=True)

    form = {
        "title": "Send Us A Message",
        "windows": [
            {"id": "contact", "classes": "", "type": "form",
             "content": form
             }
        ],
        "submit_label": "Send"
    }
    context = {
        "title": title,
        "template": "form.html",
        "args": form
    }

    return render(request, "single_content.html", context)



