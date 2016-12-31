from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^new/(?:type-(?P<competition_type>[1-5])/)?(?:league-(?P<league>[0-9]{1,9})/)?$', views.new_competition),
    url(r'^$', views.events_view),
    url(r'^(?P<pk>[0-9]{1,9})/$', views.CompetitonView.as_view(), name='competition'),
    url(r'^(?P<pk>[0-9]{1,9})/edit/$', views.CompetitonView.as_view(), name='competition_edit'),
    url(r'^olympic_events/(?P<competition_id>[0-9]{1,9})/$', views.olympic_events),
    url(r'^matchups/(?P<pk>[0-9]{1,9})/$', views.MatchupView.as_view(), name='matchup'),
    url(r'^matchups/(?P<pk>[0-9]{1,9})/edit$', views.MatchupView.as_view(), name='matchup_edit')
]
