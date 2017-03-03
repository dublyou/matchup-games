from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.get_profile, name='profile_index'),
    url(r'^(?P<pk>[0-9]{1,9})/$', views.PlayerProfileView.as_view(), name='profile'),
    url(r'^(?P<pk>[0-9]{1,9})/upcoming_matchups/$', views.upcoming_matchups, name='upcoming_matchups'),
    url(r'^(?P<pk>[0-9]{1,9})/matchup_results/$', views.matchup_results, name='matchup_results'),
    url(r'^(?P<pk>[0-9]{1,9})/competitions/$', views.my_competitions, name='my_competitions'),
    url(r'^(?P<pk>[0-9]{1,9})/invitations/$', views.player_invitations, name='player_invitations'),
    url(r'^(?P<pk>[0-9]{1,9})/edit/$', views.edit_profile, name='edit_profile'),
    url(r'^search/$', views.profile_search, name='profile_search'),
]
