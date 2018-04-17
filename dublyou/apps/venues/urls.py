from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.new_game),
    url(r'^new/$', views.new_game, name="new_game"),
    url(r'^(?P<pk>[0-9]{1,9})/$', views.GameView.as_view(), name='game'),
    url(r'^(?P<pk>[0-9]{1,9})/edit/$', views.edit_game, name='edit_game'),
]
