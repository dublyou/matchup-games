from django.conf.urls import url
from . import views

app_name = "leagues"

urlpatterns = [
    url(r'^(?P<league_id>[0-9]{1,9})/$', views.LeagueView.as_view(), name="league"),
    url(r'^new/$', views.NewLeagueView.as_view()),
    url(r'^teams/(?P<team_id>[0-9]{1,9})/$', views.TeamView.as_view(), name="team"),
    url(r'^add_members/(?P<id_type>competition|league)(?P<ref_id>[0-9]{1,9})/$',
        views.AddPlayersView.as_view()),
    url(r'^add_teams/(?P<id_type>competition|league)(?P<ref_id>[0-9]{1,9})/$',
        views.AddTeamsView.as_view()),
]
