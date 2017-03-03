# -*- coding: utf-8 -*-
from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.conf.urls.static import static
from . import views
from django.contrib.auth.views import logout

admin.site.login = login_required(admin.site.login)
urlpatterns = [
    url(r'^(?:home/)?$', views.home, name='home'),
    url(r'^bracket_builder/$', views.bracket_builder, name='bracket_builder'),
    url(r'^(?P<filename>(robots.txt)|(humans.txt))$',
        views.home_files, name='home-files'),
    url(r'^contact/$', views.contact, name='contact'),
    url(r'^admin/', admin.site.urls),
    url(r'^accounts/logout/$', logout, {'next_page': '/'}),
    url(r'^accounts/', include('allauth.urls')),
    url(r'^invitations/', include('invitations.urls')),
    url(r'^chaining/', include('smart_selects.urls')),
    url(r'^profile/', include('dublyou.apps.profile.urls')),
    url(r'^competitions/', include('dublyou.apps.competitions.urls')),
    url(r'^leagues/', include('dublyou.apps.leagues.urls')),
    url(r'^games/', include('dublyou.apps.games.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)