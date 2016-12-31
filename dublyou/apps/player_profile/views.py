# -*- coding: utf-8 -*-
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from .models import Profile
from .forms import SignUpForm, EditProfileForm, send_activation_email
from django.contrib.auth.models import User
from ...views import ProfileView, EditView
from django.utils import timezone


def get_profile(request):
    user = request.user
    if user.is_authenticated():
        return HttpResponseRedirect(user.profile.get_absolute_url())


class PlayerProfileView(ProfileView):
    model = Profile
    detail_names = ["height", "weight", "age", "current_city_state", "team_list", "league_list"]
    stat_names = []
    tab_names = ["schedule", "results"]
    toolbar = []
    image_name = "user_image"


class EditProfileView(EditView):
    form_class = EditProfileForm
    success_url = "/profile/{id}"
    form_title = "Edit Profile"


def activation(request, key):
    activation_expired = False
    already_active = False
    profile = get_object_or_404(Profile, activation_key=key)
    if not profile.user.is_active:
        if timezone.now() > profile.key_expires:
            activation_expired = True  # Display: offer the user to send a new activation link
            id_user = profile.user.id
        else:  # Activation successful
            profile.user.is_active = True
            profile.user.save()

    # If user is already active, simply display error message
    else:
        already_active = True  # Display : error message
    return render(request, 'activation.html', locals())


def new_activation_link(request, user_id):
    user = get_object_or_404(User, id=user_id)

    if user is not None and not user.is_active and request.user != user:
        send_activation_email(user, resend=True)
        request.session['new_link'] = True

    return HttpResponseRedirect('')


def sign_up(request):
    if request.method == "POST":
        form = SignUpForm(request.POST.get)
        if form.is_valid():
            form.save()
            HttpResponseRedirect('')
    else:
        form = {"title": "Sign Up",
                "id": "sign_up",
                "classes": "",
                "windows": [{"type": "form",
                             "content": SignUpForm()}
                            ],
                "submit_label": "Sign Up"
                }
        return render(request, 'my_base.html')
