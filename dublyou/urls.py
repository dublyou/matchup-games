# -*- coding: utf-8 -*-
"""dublyou URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import include, url
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    url(r'^(?:home/)?$', views.home, name='home'),
    url(r'^bracket_builder$', views.home, name='bracket_builder'),
    url(r'^(?P<filename>(robots.txt)|(humans.txt))$',
        views.home_files, name='home-files'),
    url(r'^contact/$', views.contact, name='contact'),
]

if settings.DEBUG:
    urlpatterns += [
        url(r'^admin/', admin.site.urls),
        url(r'^profile/', include('dublyou.apps.player_profile.urls', namespace='profile'), name='profile'),
        url(r'^leagues/', include('dublyou.apps.leagues.urls', namespace='league')),
        url(r'^games/', include('dublyou.apps.games.urls', namespace='game')),
        url(r'^competitions/', include('dublyou.apps.competitions.urls', namespace='competition')),
        url(r'^sign_in/$', views.sign_in, name='sign_in'),
        url(r'^sign_out/$', views.sign_out, name='sign_out'),
        url(r'^accounts/', include('allauth.urls')),
    ]
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
