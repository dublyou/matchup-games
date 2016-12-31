from django.conf.urls import url
from . import views

app_name = "player_profile"
urlpatterns = [
    url(r'^$', views.get_profile, name='index'),
    url(r'^(?P<pk>[0-9]{1,9})/$', views.PlayerProfileView.as_view(), name='detail'),
    url(r'^(?P<pk>[0-9]{1,9})/edit/$', views.PlayerProfileView.as_view(), name='edit'),
    url(r'^activate/(?P<key>[\w\d]{40})/$', views.activation, name='activate'),
    url(r'^sign_up/$', views.sign_up, name='sign_up')
]
