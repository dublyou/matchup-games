from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Profile
from django.core.mail import send_mail
from django.urls import reverse
from django.conf import settings
from django.template.loader import render_to_string
import datetime as dt
import hashlib
import random
from ...constants import DEFAULT_INPUT_CLASSES, INPUT_HTML_OUTPUT
from ...forms import MyBaseModelForm, CustomFormMixin


class SignUpForm(UserCreationForm, CustomFormMixin):
    email = forms.EmailField(label="Email", required=True, max_length=50)
    first_name = forms.CharField(label="First Name", required=True, max_length=30)
    last_name = forms.CharField(label="Last Name", required=True, max_length=30)

    def __init__(self, *args, **kwargs):
        super(UserCreationForm, self).__init__(*args, **kwargs)
        self.custom_init()

    class Meta:
        model = User
        fields = ("email", "password1", "password2", "first_name", "last_name")

    def save(self, commit=True):
        user = super(UserCreationForm, self).save(commit=False)

        user.username = self.cleaned_data["email"]
        user.email = self.cleaned_data["email"]
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        user.is_active = False

        send_mail(subject="",
                  message="",
                  from_email=settings.EMAIL_HOST_USER,
                  recipient_list=[user.email],
                  fail_silently=False)

        if commit:
            user.save()

        send_activation_email(user)

        return user


class EditProfileForm(MyBaseModelForm):
    class Meta:
        model = Profile
        fields = ['abbrev', 'mobile_number', 'birth_date', 'height', 'weight', 'gender',
                  'current_zip', 'hometown_zip', 'user_image', 'privacy_type']


def send_activation_email(user, resend=False):
    salt = hashlib.sha1(str(random.random())).hexdigest()[:5]
    activation_key = hashlib.sha1((salt + user.email).encode()).hexdigest()
    if resend:
        profile = user.profile
    else:
        profile = Profile()
        profile.user = user

    profile.activation_key = activation_key
    profile.key_expires = dt.datetime.strftime(dt.datetime.now() + dt.timedelta(days=2),
                                               "%Y-%m-%d %H:%M:%S")
    profile.save()

    link = reverse('profile:activate', args=[str(activation_key)])
    content = {'link': link, 'first_name': user.first_name}
    message = render_to_string("activation_email.html", content)
    # print unicode(message).encode('utf8')
    send_mail("Welcome to dublyou", message, 'yourdomain <no-reply@yourdomain.com>',
              [user.email], fail_silently=False)
